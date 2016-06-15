import mock
import pytest

from chiton.closet.data import CARE_TYPES
from chiton.wintour.data import BODY_SHAPES, EXPECTATION_FREQUENCIES
from chiton.wintour.matching import make_recommendations, package_wardrobe_profile


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

        expectations = sorted(pipeline_profile['expectations'], key=lambda e: e['formality'])
        assert len(expectations) == 2

        assert expectations[0] == {'formality': 'casual', 'frequency': EXPECTATION_FREQUENCIES['SOMETIMES']}
        assert expectations[1] == {'formality': 'executive', 'frequency': EXPECTATION_FREQUENCIES['OFTEN']}


@pytest.mark.django_db
class TestMakeRecommendations:

    def test_basic_recommendations(self, pipeline_profile_factory):
        """It returns raw recommendations by default."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()
        pipeline.make_recommendations.return_value = {}

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline)

        pipeline.make_recommendations.assert_called_with(profile, debug=False)

        assert recommendations == {}

    def test_debug(self, pipeline_profile_factory):
        """It generates performance metrics when called in debug mode."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()
        pipeline.make_recommendations.return_value = {}

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline, debug=True)

        pipeline.make_recommendations.assert_called_with(profile, debug=True)

        assert 'debug' in recommendations
        assert isinstance(recommendations['debug']['queries'], list)
        assert recommendations['debug']['time'] > 0
