from decimal import Decimal

import mock
import pytest

from chiton.closet.data import CARE_TYPES
from chiton.rack.models import ProductImage
from chiton.wintour.data import BODY_SHAPES, EXPECTATION_FREQUENCIES
from chiton.wintour.facets import BaseFacet
from chiton.wintour.matching import make_recommendations, package_wardrobe_profile, serialize_recommendations
from chiton.wintour.pipeline import BasicRecommendations, FacetGroup, GarmentRecommendation, Recommendations


@pytest.mark.django_db
class TestPackageWardrobeProfile:

    def test_conversion(self, wardrobe_profile_factory):
        """It transforms a profile model into a dict."""
        wardrobe_profile = wardrobe_profile_factory()
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        assert isinstance(pipeline_profile, dict)

    def test_age(self, wardrobe_profile_factory):
        """It passes the profile's age through."""
        wardrobe_profile = wardrobe_profile_factory(age=25)
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        assert pipeline_profile['age'] == 25

    def test_body_shape(self, wardrobe_profile_factory):
        """It passes the profile's body shape through."""
        wardrobe_profile = wardrobe_profile_factory(body_shape=BODY_SHAPES['PEAR'])
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        assert pipeline_profile['body_shape'] == BODY_SHAPES['PEAR']

    def test_styles(self, wardrobe_profile_factory, style_factory):
        """It uses the slugs of all styles."""
        classy = style_factory(slug='classy')
        fancy = style_factory(slug='fancy')

        wardrobe_profile = wardrobe_profile_factory(styles=[classy, fancy])
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        assert sorted(pipeline_profile['styles']) == ['classy', 'fancy']

    def test_sizes(self, wardrobe_profile_factory, standard_size_factory):
        """It uses the slugs of all sizes."""
        medium = standard_size_factory(slug='medium')
        large = standard_size_factory(slug='large')

        wardrobe_profile = wardrobe_profile_factory(sizes=[medium, large])
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        assert sorted(pipeline_profile['sizes']) == ['large', 'medium']

    def test_avoid_care(self, wardrobe_profile_factory):
        """It uses the IDs of all unwanted care types."""
        wardrobe_profile = wardrobe_profile_factory()
        wardrobe_profile.unwanted_care_types.create(care=CARE_TYPES['MACHINE_MACHINE'])
        wardrobe_profile.unwanted_care_types.create(care=CARE_TYPES['HAND_WASH'])
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        avoid_care = pipeline_profile['avoid_care']
        assert len(avoid_care) == 2
        assert CARE_TYPES['MACHINE_MACHINE'] in avoid_care
        assert CARE_TYPES['HAND_WASH'] in avoid_care

    def test_expectations(self, formality_factory, wardrobe_profile_factory):
        """It exposes formality expectations as a formality/frequency dict."""
        casual = formality_factory(slug='casual')
        executive = formality_factory(slug='executive')

        wardrobe_profile = wardrobe_profile_factory()
        wardrobe_profile.expectations.create(formality=casual, frequency=EXPECTATION_FREQUENCIES['SOMETIMES'])
        wardrobe_profile.expectations.create(formality=executive, frequency=EXPECTATION_FREQUENCIES['OFTEN'])
        pipeline_profile = package_wardrobe_profile(wardrobe_profile)

        assert pipeline_profile['expectations']['casual'] == EXPECTATION_FREQUENCIES['SOMETIMES']
        assert pipeline_profile['expectations']['executive'] == EXPECTATION_FREQUENCIES['OFTEN']


@pytest.mark.django_db
class TestMakeRecommendations:

    def test_basic_recommendations(self, pipeline_profile_factory):
        """It returns per-basic recommendations."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()
        pipeline.make_recommendations.return_value = {}

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline)

        pipeline.make_recommendations.assert_called_with(profile, debug=False)

        assert recommendations['basics'] == {}
        assert 'debug' not in recommendations

    def test_debug(self, pipeline_profile_factory):
        """It generates performance metrics when called in debug mode."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline, debug=True)

        pipeline.make_recommendations.assert_called_with(profile, debug=True)

        assert 'debug' in recommendations
        assert isinstance(recommendations['debug']['queries'], list)
        assert recommendations['debug']['time'] > 0


@pytest.mark.django_db
class TestSerializeRecommendations:

    @pytest.fixture
    def serialized(self, affiliate_item_factory, affiliate_network_factory, basic_factory, brand_factory, garment_factory):
        class TestFacet(BaseFacet):
            name = 'Test'
            slug = 'test'

        brand = brand_factory(name='Givenchy')
        blazers_basic = basic_factory(name='Blazers', slug='blazers')
        blazer_garment = garment_factory(
            basic=blazers_basic,
            brand=brand,
            name='Blazer',
            slug='blazer'
        )

        affiliate_network = affiliate_network_factory(name='Network')
        thumbnail = ProductImage.objects.create(height=10, width=10, url='http://example.net')
        blazer_item = affiliate_item_factory(
            garment=blazer_garment,
            network=affiliate_network,
            price=Decimal(10.25),
            thumbnail=thumbnail,
            url='http://example.org'
        )

        return serialize_recommendations(Recommendations({
            'basics': {
                blazers_basic: BasicRecommendations({
                    'facets': {
                        TestFacet(): [
                            FacetGroup({'count': 0, 'garment_ids': [], 'slug': 'all'}, validate=True)
                        ]
                    },
                    'garments': [GarmentRecommendation({
                        'affiliate_items': [blazer_item],
                        'explanations': {
                            'weights': [{
                                'name': 'Test',
                                'reasons': [{
                                    'reason': 'Reason',
                                    'weight': 1.0
                                }]
                            }],
                            'normalization': [{
                                'importance': 1,
                                'name': 'Test',
                                'weight': 1.0
                            }]
                        },
                        'garment': blazer_garment,
                        'weight': 1.0
                    }, validate=True)]
                }, validate=True)
            },
            'debug': {
                'queries': [{'sql': 'SELECT * FROM auth_user', 'time': 0.5}],
                'time': 2.25
            }
        }, validate=True))

    @pytest.fixture
    def serialized_blazer(self, serialized):
        return serialized['basics']['blazers']['garments'][0]

    def test_top_level(self, serialized):
        """It maintains the top-level keys of the recommendations."""
        assert 'basics' in serialized
        assert 'debug' in serialized

    def test_debug(self, serialized):
        """It preserves the debug information."""
        debug = serialized['debug']

        assert len(debug['queries']) == 1
        assert debug['queries'][0] == {
            'sql': 'SELECT * FROM auth_user',
            'time': 0.5
        }

    def test_basic_slug(self, serialized):
        """It converts basic instances to slugs."""
        basics = serialized['basics']
        assert list(basics.keys()) == ['blazers']

    def test_basic_facets(self, serialized):
        """It converts facet instances to facet slugs."""
        blazers = serialized['basics']['blazers']

        assert 'facets' in blazers
        assert blazers['facets'] == {
            'test': [
                {'count': 0, 'garment_ids': [], 'slug': 'all'}
            ]
        }

    def test_basic_garments(self, serialized):
        """It preserves the garment list."""
        assert len(serialized['basics']['blazers']['garments']) == 1

    def test_garment_affiliate_items(self, serialized_blazer):
        """It serializes affiliate items with integer-based prices and optional images."""
        assert len(serialized_blazer['affiliate_items']) == 1

        item = serialized_blazer['affiliate_items'][0]
        assert item['id'] > 0
        assert item['image'] is None
        assert item['price'] == 1025
        assert item['network_name'] == 'Network'
        assert item['thumbnail'] == {
            'height': 10,
            'url': 'http://example.net',
            'width': 10
        }
        assert item['url'] == 'http://example.org'

    def test_garment_explanations(self, serialized_blazer):
        """It preserves garment explanations."""
        assert serialized_blazer['explanations'] == {
            'weights': [{
                'name': 'Test',
                'reasons': [{
                    'reason': 'Reason',
                    'weight': 1.0
                }]
            }],
            'normalization': [{
                'importance': 1,
                'name': 'Test',
                'weight': 1.0
            }]
        }

    def test_garment_data(self, serialized_blazer):
        """It exposes a simplified subset of the garment's data."""
        garment = serialized_blazer['garment']

        assert garment['brand'] == 'Givenchy'
        assert garment['name'] == 'Blazer'

        assert garment['id'] > 0

    def test_garment_weight(self, serialized_blazer):
        """It preserves the floating-point weight."""
        assert serialized_blazer['weight'] == 1.0
