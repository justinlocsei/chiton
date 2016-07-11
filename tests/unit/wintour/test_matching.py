import mock
import pytest

from chiton.wintour.matching import make_recommendations


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
