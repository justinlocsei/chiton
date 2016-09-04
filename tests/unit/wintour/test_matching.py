import mock
import pytest

from chiton.core.exceptions import FormatError
from chiton.wintour.matching import convert_recommendation_to_wardrobe_profile, make_recommendations, PersonRecommendation


@pytest.mark.django_db
class TestConvertRecommendationToWardrobeProfile:

    @pytest.fixture
    def convert_recommendation(self, pipeline_profile_factory, recommendation_factory):
        def perform_conversion(**profile_data):
            profile = pipeline_profile_factory(**profile_data)
            recommendation = recommendation_factory(profile=profile)
            return convert_recommendation_to_wardrobe_profile(recommendation)

        return perform_conversion

    def test_conversion(self, convert_recommendation):
        """It converts a recommendation to a wardrobe profile."""
        converted = convert_recommendation()
        assert converted.pk

    def test_converts_birth_year(self, convert_recommendation):
        """It converts the birth year."""
        converted = convert_recommendation(birth_year=2012)
        assert converted.birth_year == 2012

    def test_converts_body_shape(self, convert_recommendation):
        """It converts the body shape."""
        converted = convert_recommendation(body_shape='apple')
        assert converted.body_shape == 'apple'

    def test_converts_styles(self, convert_recommendation, style_factory):
        """It converts the style slugs to style relations."""
        classy = style_factory(slug='classy')
        formal = style_factory(slug='formal')
        sassy = style_factory(slug='sassy')

        converted = convert_recommendation(styles=['classy', 'formal'])
        assert converted.styles.count() == 2

        style_ids = converted.styles.values_list('pk', flat=True)
        assert classy.pk in style_ids
        assert formal.pk in style_ids
        assert sassy.pk not in style_ids

    def test_converts_sizes(self, convert_recommendation, standard_size_factory):
        """It converts the size slugs to size relations."""
        small = standard_size_factory(slug='small')
        medium = standard_size_factory(slug='medium')
        large = standard_size_factory(slug='large')

        converted = convert_recommendation(sizes=['small', 'medium'])
        assert converted.sizes.count() == 2

        size_ids = converted.sizes.values_list('pk', flat=True)
        assert small.pk in size_ids
        assert medium.pk in size_ids
        assert large.pk not in size_ids

    def test_converts_formalities(self, convert_recommendation, formality_factory):
        """It converts the formality objects into expectation relations."""
        casual = formality_factory(slug='casual')
        executive = formality_factory(slug='executive')

        converted = convert_recommendation(expectations=[
            {'formality': 'casual', 'frequency': 'always'},
            {'formality': 'executive', 'frequency': 'never'}
        ])
        assert converted.expectations.count() == 2

        expectations = converted.expectations.all().order_by('frequency')

        ex_casual = expectations[0]
        assert ex_casual.formality == casual
        assert ex_casual.frequency == 'always'

        ex_executive = expectations[1]
        assert ex_executive.formality == executive
        assert ex_executive.frequency == 'never'

    def test_converts_care_types(self, convert_recommendation):
        """It converts the care-type slugs to relations."""
        converted = convert_recommendation(avoid_care=['hand_wash'])

        care_types = converted.unwanted_care_types.values_list('care', flat=True)
        assert list(care_types) == ['hand_wash']

    def test_converts_care_types_empty(self, convert_recommendation):
        """It handle empty care-type avoidances."""
        converted = convert_recommendation(avoid_care=[])
        assert not converted.unwanted_care_types.count()

    def test_adds_person(self, pipeline_profile_factory, recommendation_factory, person_factory):
        """It can associate a person with the recommendation."""
        profile = pipeline_profile_factory()
        recommendation = recommendation_factory(profile=profile)
        person = person_factory()

        no_person = convert_recommendation_to_wardrobe_profile(recommendation)
        with_person = convert_recommendation_to_wardrobe_profile(recommendation, person=person)

        assert not no_person.person
        assert with_person.person == person

    def test_binds_recommendation(self, pipeline_profile_factory, recommendation_factory):
        """It can associate a person with the recommendation."""
        profile = pipeline_profile_factory()
        recommendation = recommendation_factory(profile=profile)

        converted = convert_recommendation_to_wardrobe_profile(recommendation)
        assert converted.recommendation == recommendation


@pytest.mark.django_db
class TestMakeRecommendations:

    def test_basic_recommendations(self, pipeline_profile_factory):
        """It returns raw recommendations by default."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()
        pipeline.make_recommendations.return_value = {}

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline)

        pipeline.make_recommendations.assert_called_with(profile, debug=False, max_garments_per_group=None)

        assert recommendations == {}

    def test_debug(self, pipeline_profile_factory):
        """It generates performance metrics when called in debug mode."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()
        pipeline.make_recommendations.return_value = {}

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline, debug=True, max_garments_per_group=None)

        pipeline.make_recommendations.assert_called_with(profile, debug=True, max_garments_per_group=None)

        assert 'debug' in recommendations
        assert isinstance(recommendations['debug']['queries'], list)
        assert recommendations['debug']['time'] > 0

    def test_max_garments_per_group(self, pipeline_profile_factory):
        """It passes an optional garment cap to the pipeline."""
        pipeline = mock.Mock()
        pipeline.make_recommendations = mock.MagicMock()
        pipeline.make_recommendations.return_value = {}

        profile = pipeline_profile_factory()
        recommendations = make_recommendations(profile, pipeline, max_garments_per_group=5)

        pipeline.make_recommendations.assert_called_with(profile, debug=False, max_garments_per_group=5)

        assert recommendations == {}


@pytest.mark.django_db
class TestPersonRecommendation:

    @pytest.fixture
    def valid_recommendation(self):
        return {
            'email': 'test@example.com',
            'recommendation_id': 1
        }

    def test_valid(self, valid_recommendation):
        """It accepts data with a valid format."""
        assert PersonRecommendation(valid_recommendation)

    def test_email(self, valid_recommendation):
        """It requires a valid email address."""
        valid_recommendation['email'] = 'example.com'
        with pytest.raises(FormatError):
            PersonRecommendation(valid_recommendation)

    def test_recommendation_id(self, valid_recommendation):
        """It requires a number."""
        valid_recommendation['recommendation_id'] = '1'
        with pytest.raises(FormatError):
            PersonRecommendation(valid_recommendation)
