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
