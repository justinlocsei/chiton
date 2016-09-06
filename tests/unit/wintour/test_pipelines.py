from decimal import Decimal

import pytest

from chiton.closet.data import CARE_TYPES
from chiton.wintour.facets import BaseFacet
from chiton.wintour.garment_filters import BaseGarmentFilter
from chiton.wintour.pipeline import FacetGroup
from chiton.wintour.pipelines import BasePipeline
from chiton.wintour.query_filters import BaseQueryFilter
from chiton.wintour.weights import BaseWeight


class DummyQueryFilter(BaseQueryFilter):
    name = 'Test Query Filter'
    slug = 'test-query-filter'


class DummyGarmentFilter(BaseGarmentFilter):
    name = 'Test Garment Filter'
    slug = 'test-garment-filter'


class DummyWeight(BaseWeight):
    name = 'Test Weight'
    slug = 'test-weight'


class DummyFacet(BaseFacet):
    name = 'Test Facet'
    slug = 'test-face'


@pytest.fixture
def pipeline_factory():
    def create_pipeline(query_filters=[], garment_filters=[], weights=[], facets=[]):
        class Pipeline(BasePipeline):

            def provide_query_filters(self):
                return query_filters

            def provide_garment_filters(self):
                return garment_filters

            def provide_weights(self):
                return weights or [DummyWeight()]

            def provide_facets(self):
                return facets

        return Pipeline()

    return create_pipeline


@pytest.mark.django_db
class TestBasePipeline:

    def test_provide_garments(self, garment_factory):
        """It provides the full queryset of garments."""
        garment_factory()
        garment_factory()

        garments = BasePipeline().provide_garments()

        assert garments.count() == 2

    def test_load_garments(self, garment_factory, pipeline_factory):
        """It allows each pipeline step to modify the garment queryset."""
        def slice_garments(garments):
            return garments[:garments.count() - 1]

        class QueryFilter(DummyQueryFilter):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        class GarmentFilter(DummyGarmentFilter):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        class Weight(DummyWeight):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        class Facet(DummyFacet):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        pipeline = pipeline_factory(
            query_filters=[QueryFilter()],
            garment_filters=[GarmentFilter()],
            weights=[Weight()],
            facets=[Facet()]
        )

        for i in range(0, 5):
            garment_factory()

        garments = pipeline.load_garments()
        assert garments.count() == 1

    def test_make_recommendations(self, basic_factory, brand_factory, category_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It produces per-basic garment recommendations for a wardrobe profile."""
        class QueryFilter(DummyQueryFilter):
            def apply(self, garments):
                return garments.exclude(name='3')

        class GarmentFilter(DummyGarmentFilter):
            def apply(self, garment):
                return garment.name == '2'

        class Weight(DummyWeight):
            def apply(self, garment):
                return int(garment.name)

        class Facet(DummyFacet):
            name = 'Facet'
            slug = 'test'

            def apply(self, basic, garments):
                return [FacetGroup({
                    'garment_ids': [g['garment']['id'] for g in garments],
                    'slug': 'all'
                })]

        skirts = basic_factory(slug='skirt', name='Skirt', plural_name='Skirts', category=category_factory(name='Lower Torso'))
        shirts = basic_factory(slug='shirt', name='Shirt', plural_name='Shirts', category=category_factory(name='Upper Torso'))

        brand_one = brand_factory(name='Brand 1')
        brand_two = brand_factory(name='Brand 2')

        skirt_one = garment_factory(basic=skirts, brand=brand_one, name='1', care=CARE_TYPES['DRY_CLEAN'])
        skirt_two = garment_factory(basic=skirts, brand=brand_one, name='2')
        skirt_three = garment_factory(basic=skirts, brand=brand_one, name='3')
        shirt_one = garment_factory(basic=shirts, brand=brand_two, name='1')
        shirt_four = garment_factory(basic=shirts, brand=brand_two, name='4')

        affiliate_item_factory(garment=skirt_one)
        affiliate_item_factory(garment=skirt_two)
        affiliate_item_factory(garment=skirt_three)
        affiliate_item_factory(garment=shirt_one)
        affiliate_item_factory(garment=shirt_four)

        facet = Facet()
        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(
            query_filters=[QueryFilter()],
            garment_filters=[GarmentFilter()],
            weights=[Weight()],
            facets=[facet]
        )

        recommendations = pipeline.make_recommendations(profile)
        assert set(recommendations.keys()) == set(['basics', 'categories'])

        assert len(recommendations['basics']) == 2
        shirt_recs = recommendations['basics'][0]
        skirt_recs = recommendations['basics'][1]

        assert skirt_recs['basic']['name'] == 'Skirt'
        assert skirt_recs['basic']['plural_name'] == 'Skirts'
        assert skirt_recs['basic']['slug'] == 'skirt'
        assert skirt_recs['basic']['category'] == 'Lower Torso'

        assert shirt_recs['basic']['name'] == 'Shirt'
        assert shirt_recs['basic']['plural_name'] == 'Shirts'
        assert shirt_recs['basic']['slug'] == 'shirt'
        assert shirt_recs['basic']['category'] == 'Upper Torso'

        assert [g['weight'] for g in skirt_recs['garments']] == [0.25]
        skirt_one_rec = skirt_recs['garments'][0]['garment']
        assert skirt_one_rec['id'] > 0
        assert skirt_one_rec['name'] == '1'
        assert skirt_one_rec['brand'] == 'Brand 1'
        assert skirt_one_rec['care'] == 'Dry clean'

        assert [g['weight'] for g in shirt_recs['garments']] == [1.0, 0.25]
        shirt_four_rec = shirt_recs['garments'][0]['garment']
        shirt_one_rec = shirt_recs['garments'][1]['garment']

        assert shirt_one_rec['id'] > 0
        assert shirt_one_rec['name'] == '1'
        assert shirt_one_rec['brand'] == 'Brand 2'
        assert shirt_one_rec['branded_name'] == 'Brand 2 1'
        assert shirt_one_rec['care'] is None

        assert shirt_four_rec['id'] > 0
        assert shirt_four_rec['name'] == '4'
        assert shirt_four_rec['brand'] == 'Brand 2'
        assert shirt_four_rec['branded_name'] == 'Brand 2 4'

        assert len(skirt_recs['facets']) == 1
        assert len(shirt_recs['facets']) == 1
        skirt_facets = skirt_recs['facets'][0]
        shirt_facets = shirt_recs['facets'][0]

        assert skirt_facets['name'] == 'Facet'
        assert skirt_facets['slug'] == 'test'
        assert len(skirt_facets['groups']) == 1
        assert skirt_facets['groups'][0]['garment_ids'] == [skirt_one.pk]

        assert shirt_facets['name'] == 'Facet'
        assert shirt_facets['slug'] == 'test'
        assert len(shirt_facets['groups']) == 1
        assert set(shirt_facets['groups'][0]['garment_ids']) == set([shirt_four.pk, shirt_one.pk])

    def test_make_recommendations_categories(self, category_factory, pipeline_factory, pipeline_profile_factory):
        """It exposes the ordered categories."""
        category_factory(name='Pants', position=2)
        category_factory(name='Skirts', position=1)

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory()
        recommendations = pipeline.make_recommendations(profile)

        assert recommendations['categories'] == ['Skirts', 'Pants']

    def test_make_recommendations_affiliate_items(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It exposes information on each garment's available affiliate items, sorted by price."""
        class Weight(DummyWeight):
            def apply(self, garment):
                return int(garment.name)

        basic = basic_factory()
        garment_single = garment_factory(basic=basic, name='1')
        garment_multi = garment_factory(basic=basic, name='2')

        item_one_one = affiliate_item_factory(garment=garment_single)
        item_two_one = affiliate_item_factory(garment=garment_multi, price=Decimal(10))
        item_two_two = affiliate_item_factory(garment=garment_multi, price=Decimal(20))

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[Weight()])
        recommendations = pipeline.make_recommendations(profile)

        assert len(recommendations['basics']) == 1
        garments = recommendations['basics'][0]['garments']

        assert len(garments) == 2
        assert [g['garment']['name'] for g in garments] == ['2', '1']

        garment_multi_items = garments[0]['purchase_options']
        assert len(garment_multi_items) == 2
        assert [i['id'] for i in garment_multi_items] == [item_two_two.id, item_two_one.id]

        garment_single_items = garments[1]['purchase_options']
        assert len(garment_single_items) == 1
        assert garment_single_items[0]['id'] == item_one_one.id

    def test_make_recommendations_affiliate_items_serialized(self, basic_factory, affiliate_item_factory, affiliate_network_factory, garment_factory, pipeline_factory, pipeline_profile_factory, item_image_factory):
        """It serializes each affiliate item, with optional image data."""
        basic = basic_factory()
        garment = garment_factory(basic=basic)
        network = affiliate_network_factory(name='Network')

        with_images = affiliate_item_factory(network=network, garment=garment, affiliate_url='http://example.com/with', price=Decimal(100), retailer='Amazon', has_multiple_colors=False)
        affiliate_item_factory(network=network, garment=garment, affiliate_url='http://example.com/without', price=Decimal(15.25), retailer='Nordstrom', has_multiple_colors=True)

        item_image_factory(item=with_images, height=100, width=100, file_name='image.jpg')
        item_image_factory(item=with_images, height=50, width=50, file_name='thumbnail.jpg')

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory()

        recommendations = pipeline.make_recommendations(profile)
        items = recommendations['basics'][0]['garments'][0]['purchase_options']

        with_data = items[0]
        assert with_data['price'] == 10000
        assert with_data['network_name'] == 'Network'
        assert with_data['retailer'] == 'Amazon'
        assert with_data['id'] > 0
        assert not with_data['has_multiple_colors']
        assert with_data['url'] == 'http://example.com/with'
        assert len(with_data['images']) == 2

        image_data = with_data['images'][0]
        assert image_data['height'] == 100
        assert image_data['width'] == 100
        assert image_data['url'].endswith('/image.jpg')

        thumbnail_data = with_data['images'][1]
        assert thumbnail_data['height'] == 50
        assert thumbnail_data['width'] == 50
        assert thumbnail_data['url'].endswith('/thumbnail.jpg')

        without_data = items[1]
        assert without_data['price'] == 1525
        assert without_data['network_name'] == 'Network'
        assert without_data['retailer'] == 'Nordstrom'
        assert without_data['id'] > 0
        assert without_data['has_multiple_colors']
        assert without_data['url'] == 'http://example.com/without'
        assert not len(without_data['images'])

    def test_make_recommendations_queryset_filters(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It combines all queryset filters."""
        class TallFilter(DummyQueryFilter):
            def apply(self, garments):
                return garments.filter(is_tall_sized=False)

        class PetiteFilter(DummyQueryFilter):
            def apply(self, garments):
                return garments.filter(is_petite_sized=False)

        basic = basic_factory()
        affiliate_item_factory(garment=garment_factory(basic=basic, is_regular_sized=True))
        affiliate_item_factory(garment=garment_factory(basic=basic, is_petite_sized=True))
        affiliate_item_factory(garment=garment_factory(basic=basic, is_tall_sized=True))

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(query_filters=[TallFilter(), PetiteFilter()])

        recommendations = pipeline.make_recommendations(profile)

        assert len(recommendations['basics'][0]['garments']) == 1

    def test_make_recommendations_garment_filters(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It combines all garment filters."""
        class PantsFilter(DummyGarmentFilter):
            def apply(self, garment):
                return garment.name == 'Pants'

        class ShirtFilter(DummyGarmentFilter):
            def apply(self, garment):
                return garment.name == 'Shirt'

        class CombinedFilter(DummyGarmentFilter):
            def apply(self, garment):
                return garment.name in ['Pants', 'Shirt']

        basic = basic_factory()
        affiliate_item_factory(garment=garment_factory(basic=basic, name='Dress'))
        affiliate_item_factory(garment=garment_factory(basic=basic, name='Pants'))
        affiliate_item_factory(garment=garment_factory(basic=basic, name='Shirt'))

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(garment_filters=[PantsFilter(), ShirtFilter(), CombinedFilter()])

        recommendations = pipeline.make_recommendations(profile)

        assert len(recommendations['basics'][0]['garments']) == 1

    def test_make_recommendations_weights_normalization(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It normalizes a single weight's range of values as floating-point percentage sorted in descending order."""
        class Weight(DummyWeight):
            def apply(self, garment):
                return int(garment.name)

        basic = basic_factory()
        positive_garment = garment_factory(basic=basic, name='100')
        negative_garment = garment_factory(basic=basic, name='-100')
        zero_garment = garment_factory(basic=basic, name='0')

        affiliate_item_factory(garment=positive_garment)
        affiliate_item_factory(garment=negative_garment)
        affiliate_item_factory(garment=zero_garment)

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[Weight()])

        recommendations = pipeline.make_recommendations(profile)

        garments = recommendations['basics'][0]['garments']
        assert len(garments) == 3

        weights_by_garment = {}
        for garment in garments:
            weights_by_garment[garment['garment']['name']] = garment['weight']

        assert weights_by_garment['100'] == 1.0
        assert weights_by_garment['-100'] == 0.0
        assert weights_by_garment['0'] == 0.5

        assert [g['weight'] for g in garments] == [1.0, 0.5, 0.0]

    def test_make_recommendations_weights_coalesce(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It combines multiple weights for a garment into per-garment normalized weights."""
        class ConstantWeight(DummyWeight):
            def apply(self, garment):
                return int(garment.name)

        class AbsoluteWeight(DummyWeight):
            def apply(self, garment):
                return abs(int(garment.name))

        basic = basic_factory()
        positive_garment = garment_factory(basic=basic, name='1')
        negative_garment = garment_factory(basic=basic, name='-1')

        affiliate_item_factory(garment=positive_garment)
        affiliate_item_factory(garment=negative_garment)

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[AbsoluteWeight(importance=3), ConstantWeight()])

        recommendations = pipeline.make_recommendations(profile)

        weights_by_garment = {}
        for garment in recommendations['basics'][0]['garments']:
            weights_by_garment[garment['garment']['name']] = garment['weight']

        assert weights_by_garment['1'] == 1.0
        assert weights_by_garment['-1'] == 0.75

    def test_make_recommendations_weights_debug(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It adds debugging information for weights when requested."""
        class Weight(DummyWeight):
            name = 'Custom Weight'

            def apply(self, garment):
                if self.debug:
                    self.explain_weight(garment, 2.0, "Constant weight")
                return 2.0

        basic = basic_factory()
        affiliate_item_factory(garment=garment_factory(basic=basic))

        query_filter = DummyQueryFilter()
        garment_filter = DummyGarmentFilter()
        facet = DummyFacet()
        weight = Weight()

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(
            query_filters=[query_filter],
            garment_filters=[garment_filter],
            weights=[weight],
            facets=[facet]
        )

        recommendations = pipeline.make_recommendations(profile, debug=True)
        garments = recommendations['basics'][0]['garments']

        assert len(garments) == 1

        explanations = garments[0]['explanations']
        normalization = explanations['normalization']
        weights = explanations['weights']

        assert len(normalization) == 1
        assert len(weights) == 1

        normalized = normalization[0]
        assert normalized['importance'] == 1
        assert normalized['weight'] == 1.0
        assert normalized['name'] == 'Custom Weight'

        weighted = weights[0]
        assert weighted['name'] == 'Custom Weight'
        assert len(weighted['reasons']) == 1

        reason = weighted['reasons'][0]
        assert reason['reason'] == 'Constant weight'
        assert reason['weight'] == 2.0

    def test_make_recommendations_facets(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It creates facets for the final recommendations."""
        class NameFacet(DummyFacet):
            name = 'Name'
            slug = 'name'

            def apply(self, basic, garments):
                gs = [g['garment'] for g in garments]
                return [
                    FacetGroup({
                        'garment_ids': [g['id'] for g in gs if g['name'] == 'Shirt'],
                        'slug': 'low'
                    }),
                    FacetGroup({
                        'garment_ids': [g['id'] for g in gs if g['name'] == 'Jeans'],
                        'slug': 'high'
                    })
                ]

        basic = basic_factory()
        shirt = garment_factory(basic=basic, name='Shirt')
        jeans = garment_factory(basic=basic, name='Jeans')

        affiliate_item_factory(garment=shirt)
        affiliate_item_factory(garment=jeans)

        name_facet = NameFacet()
        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(facets=[name_facet])

        recommendations = pipeline.make_recommendations(profile)
        facets = recommendations['basics'][0]['facets']

        assert len(facets) == 1
        assert facets[0]['name'] == 'Name'
        assert facets[0]['slug'] == 'name'
        name_facets = facets[0]['groups']

        assert len(name_facets) == 2
        assert name_facets[0]['slug'] == 'low'
        assert name_facets[1]['slug'] == 'high'

        assert name_facets[0]['garment_ids'] == [shirt.pk]
        assert name_facets[1]['garment_ids'] == [jeans.pk]

    def test_make_recommendations_max_garments_per_group(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory, brand_factory):
        """It allows a maximum number of garments to be set per facet group, sorting by weight and name."""
        class LengthWeight(DummyWeight):
            def apply(self, garment):
                return len(garment.name)

        class NameFacet(DummyFacet):
            name = 'Name'
            slug = 'name'

            def apply(self, basic, garments):
                gs = [g['garment'] for g in garments]
                return [
                    FacetGroup({
                        'garment_ids': [g['id'] for g in gs if g['name'].startswith('S')],
                        'slug': 's'
                    }),
                    FacetGroup({
                        'garment_ids': [g['id'] for g in gs if g['name'].startswith('J')],
                        'slug': 'j'
                    })
                ]

        basic = basic_factory()
        brand = brand_factory()

        shirt = garment_factory(basic=basic, name='Shirt', brand=brand)
        sweater = garment_factory(basic=basic, name='Sweater', brand=brand)
        swatter = garment_factory(basic=basic, name='Swatter', brand=brand)
        sneakers = garment_factory(basic=basic, name='Sneakers', brand=brand)
        jeans = garment_factory(basic=basic, name='Jeans', brand=brand)

        affiliate_item_factory(garment=shirt)
        affiliate_item_factory(garment=sweater)
        affiliate_item_factory(garment=swatter)
        affiliate_item_factory(garment=sneakers)
        affiliate_item_factory(garment=jeans)

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[LengthWeight()], facets=[NameFacet()])

        recommendations = pipeline.make_recommendations(profile, max_garments_per_group=2)
        for_basic = recommendations['basics'][0]
        facets = for_basic['facets']
        name_facets = facets[0]['groups']

        assert len(name_facets) == 2
        assert name_facets[0]['slug'] == 's'
        assert name_facets[1]['slug'] == 'j'

        assert name_facets[0]['garment_ids'] == [sneakers.pk, swatter.pk]
        assert name_facets[1]['garment_ids'] == [jeans.pk]

        assert set([g['garment']['id'] for g in for_basic['garments']]) == set([sneakers.pk, swatter.pk, jeans.pk])

    def test_make_recommendations_empty(self, pipeline_profile_factory):
        """It returns empty recommendations for a default pipeline."""
        profile = pipeline_profile_factory()
        pipeline = BasePipeline()

        assert pipeline.make_recommendations(profile) == {
            'basics': [],
            'categories': []
        }
