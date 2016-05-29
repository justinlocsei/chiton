import pytest

from chiton.closet.data import EMPHASES, PANT_RISES
from chiton.core.exceptions import ConfigurationError
from chiton.wintour.data import BODY_SHAPES, IMPORTANCES
from chiton.wintour.pipeline import PipelineProfile
from chiton.wintour.weights.body_shape import BodyShapeWeight


@pytest.fixture
def metrics_factory():
    def factory(custom={}):
        defaults = {
            'shoulder': {
                'emphasis': EMPHASES['NEUTRAL'],
                'importance': IMPORTANCES['MEDIUM']
            },
            'waist': {
                'emphasis': EMPHASES['NEUTRAL'],
                'importance': IMPORTANCES['MEDIUM']
            },
            'hip': {
                'emphasis': EMPHASES['NEUTRAL'],
                'importance': IMPORTANCES['MEDIUM']
            },
            'pant_rises': (PANT_RISES['NORMAL'],)
        }
        defaults.update(custom)
        return defaults

    return factory


@pytest.mark.django_db
class TestBodyShapeWeight:

    def test_metrics(self, metrics_factory):
        """It expects a list of metrics for body shapes."""
        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['APPLE']: metrics_factory()
        })

        assert weight.metrics

    def test_metrics_validation_shapes(self, metrics_factory):
        """It raises an error when the metrics use an unknown body-shape key."""
        with pytest.raises(ConfigurationError):
            BodyShapeWeight(metrics={
                'invalid': metrics_factory()
            })

    def test_metrics_validation_structure(self, metrics_factory):
        """It raises an error when the metrics use an invalid format for a shape's data."""
        with pytest.raises(ConfigurationError):
            BodyShapeWeight(metrics={
                BODY_SHAPES['APPLE']: metrics_factory({'shoulder': {'importance': 'invalid'}})
            })

        with pytest.raises(ConfigurationError):
            BodyShapeWeight(metrics={
                BODY_SHAPES['APPLE']: metrics_factory({'hip': {'emphasis': 'invalid'}})
            })

        with pytest.raises(ConfigurationError):
            BodyShapeWeight(metrics={
                BODY_SHAPES['APPLE']: metrics_factory({'waist': 'value'})
            })

        with pytest.raises(ConfigurationError):
            BodyShapeWeight(metrics={
                BODY_SHAPES['APPLE']: metrics_factory({'pant_rises': ('invalid',)})
            })

    def test_matches_emphasis(self, garment_factory, metrics_factory):
        """It applies weights based on how ideally a garment's body-part emphasis matches the ideal."""
        weak_hip = garment_factory(hip_emphasis=EMPHASES['WEAK'])
        neutral_hip = garment_factory(hip_emphasis=EMPHASES['NEUTRAL'])
        strong_hip = garment_factory(hip_emphasis=EMPHASES['STRONG'])

        profile = PipelineProfile(body_shape=BODY_SHAPES['PEAR'])
        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['PEAR']: metrics_factory({
                'hip': {
                    'emphasis': EMPHASES['WEAK'],
                    'importance': IMPORTANCES['MEDIUM']
                }
            })
        })

        with weight.apply_to_profile(profile) as apply_fn:
            weak_result = apply_fn(weak_hip)
            neutral_result = apply_fn(neutral_hip)
            strong_result = apply_fn(strong_hip)

        assert weak_result > neutral_result > strong_result
        assert strong_result

    def test_matches_emphasis_midpoint(self, garment_factory, metrics_factory):
        """It applies equal, lesser weights to misses when a neutral emphasis is ideal."""
        weak_shoulders = garment_factory(shoulder_emphasis=EMPHASES['WEAK'])
        neutral_shoulders = garment_factory(shoulder_emphasis=EMPHASES['NEUTRAL'])
        strong_shoulders = garment_factory(shoulder_emphasis=EMPHASES['STRONG'])

        profile = PipelineProfile(body_shape=BODY_SHAPES['PEAR'])
        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['PEAR']: metrics_factory({
                'shoulder': {
                    'emphasis': EMPHASES['NEUTRAL'],
                    'importance': IMPORTANCES['MEDIUM']
                }
            })
        })

        with weight.apply_to_profile(profile) as apply_fn:
            weak_result = apply_fn(weak_shoulders)
            neutral_result = apply_fn(neutral_shoulders)
            strong_result = apply_fn(strong_shoulders)

        assert neutral_result > weak_result
        assert neutral_result > strong_result
        assert weak_result == strong_result
        assert weak_result

    def test_matches_emphasis_importance(self, garment_factory, metrics_factory):
        """It modifies emphasis weights based on their importance."""
        neutral_waist = garment_factory(waist_emphasis=EMPHASES['NEUTRAL'])
        profile = PipelineProfile(body_shape=BODY_SHAPES['PEAR'])

        results = {}
        for importance in ('low', 'medium', 'high'):
            weight = BodyShapeWeight(metrics={
                BODY_SHAPES['PEAR']: metrics_factory({
                    'waist': {
                        'emphasis': EMPHASES['NEUTRAL'],
                        'importance': IMPORTANCES[importance.upper()]
                    }
                })
            })

            with weight.apply_to_profile(profile) as apply_fn:
                results[importance] = apply_fn(neutral_waist)

        assert results['low'] < results['medium'] < results['high']
        assert results['low']

    def test_matches_pant_rises(self, garment_factory, metrics_factory):
        """It adds a constant weight for garments whose pant rise flatters the user's body shape."""
        low_rise = garment_factory(pant_rise=PANT_RISES['LOW'])
        normal_rise = garment_factory(pant_rise=PANT_RISES['NORMAL'])
        high_rise = garment_factory(pant_rise=PANT_RISES['HIGH'])

        profile = PipelineProfile(body_shape=BODY_SHAPES['PEAR'])
        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['PEAR']: metrics_factory({
                'pant_rises': (PANT_RISES['LOW'], PANT_RISES['NORMAL'])
            })
        })

        with weight.apply_to_profile(profile) as apply_fn:
            low_result = apply_fn(low_rise)
            normal_result = apply_fn(normal_rise)
            high_result = apply_fn(high_rise)

        assert low_result == normal_result
        assert high_result < low_result

    def test_matches_metrics_shape(self, garment_factory, metrics_factory):
        """It uses shape-specific metrics to make recommendations."""
        neutral_waist = garment_factory(waist_emphasis=EMPHASES['NEUTRAL'])

        pear_profile = PipelineProfile(body_shape=BODY_SHAPES['PEAR'])
        apple_profile = PipelineProfile(body_shape=BODY_SHAPES['APPLE'])

        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['APPLE']: metrics_factory({
                'waist': {
                    'emphasis': EMPHASES['STRONG'],
                    'importance': IMPORTANCES['MEDIUM']
                }
            }),
            BODY_SHAPES['PEAR']: metrics_factory({
                'waist': {
                    'emphasis': EMPHASES['NEUTRAL'],
                    'importance': IMPORTANCES['MEDIUM']
                }
            }),
        })

        with weight.apply_to_profile(pear_profile) as apply_fn:
            pear_result = apply_fn(neutral_waist)

        with weight.apply_to_profile(apple_profile) as apply_fn:
            apple_result = apply_fn(neutral_waist)

        assert pear_result > apple_result
        assert apple_result

    def test_debug(self, garment_factory, metrics_factory):
        """It logs explanations for all garments, with more messages for pant-rise matches."""
        garment_shape = garment_factory(hip_emphasis=EMPHASES['STRONG'])
        garment_pants = garment_factory(pant_rise=PANT_RISES['LOW'])

        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['HOURGLASS']: metrics_factory({
                'hip': {
                    'emphasis': EMPHASES['STRONG'],
                    'importance': IMPORTANCES['MEDIUM']
                },
                'pant_rises': (PANT_RISES['LOW'],)
            })
        })
        weight.debug = True

        profile = PipelineProfile(body_shape=BODY_SHAPES['HOURGLASS'])
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment_shape)
            apply_fn(garment_pants)

        shape_messages = weight.get_explanations(garment_shape)
        pant_messages = weight.get_explanations(garment_pants)

        assert shape_messages
        assert pant_messages
        assert len(pant_messages) > len(shape_messages)

    def test_debug_flag(self, garment_factory, metrics_factory):
        """It does not log explanations when debug mode is not enabled."""
        garment = garment_factory(pant_rise=PANT_RISES['LOW'])

        weight = BodyShapeWeight(metrics={
            BODY_SHAPES['HOURGLASS']: metrics_factory({
                'pant_rises': (PANT_RISES['LOW'],)
            })
        })

        profile = PipelineProfile(body_shape=BODY_SHAPES['HOURGLASS'])
        with weight.apply_to_profile(profile) as apply_fn:
            apply_fn(garment)

        assert not weight.get_explanations(garment)
