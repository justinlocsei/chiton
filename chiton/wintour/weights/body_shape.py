import voluptuous as V

from chiton.closet.data import EMPHASES, EMPHASIS_DISPLAY, PANT_RISES
from chiton.core.exceptions import FormatError
from chiton.core.schema import OneOf
from chiton.wintour.data import BODY_SHAPES, BODY_SHAPE_DISPLAY, IMPORTANCES
from chiton.wintour.weights import BaseWeight


# A mapping of internal emphasis keys to fields on the Garment model
EMPHASIS_FIELDS = {
    'hip': 'hip_emphasis',
    'shoulder': 'shoulder_emphasis',
    'waist': 'waist_emphasis'
}

# A mapping of steps away from the ideal emphasis to a readable adjective
EMPHASIS_DELTA_STATES = {
    0: 'great',
    1: 'good',
    2: 'bad'
}

# A mapping of emphases to their numeric weight
EMPHASIS_RANKS = {
    EMPHASES['WEAK']: 0,
    EMPHASES['NEUTRAL']: 1,
    EMPHASES['STRONG']: 2
}

# A mapping of importances to readable values
IMPORTANCE_DISPLAY = {
    IMPORTANCES['LOW']: 'low',
    IMPORTANCES['MEDIUM']: 'medium',
    IMPORTANCES['HIGH']: 'high'
}

# Schemas for validating metrics
IDEAL_SCHEMA = V.Schema({
    V.Required('emphasis'): OneOf(EMPHASES.values()),
    V.Required('importance'): OneOf(IMPORTANCES.values())
})
METRICS_SCHEMA = V.Schema({
    V.Required('hip'): IDEAL_SCHEMA,
    V.Required('pant_rises'): tuple(PANT_RISES.values()),
    V.Required('shoulder'): IDEAL_SCHEMA,
    V.Required('waist'): IDEAL_SCHEMA
})


class BodyShapeWeight(BaseWeight):
    """A weight that compares a user's body shape with a garment's cut."""

    name = 'Body shape'
    slug = 'body-shape'

    def configure_weight(self, metrics=None):
        """Configure the weight with specific body-shape metrics.

        Keyword Args:
            metrics (dict): The body-shape metrics used to make recommendations

        Raises:
            chiton.core.exceptions.FormatError: If the metrics are invalid
        """
        self.metrics = self._validate_metrics(metrics)

    def provide_profile_data(self, profile):
        return {
            'body_shape': BODY_SHAPE_DISPLAY[profile['body_shape']],
            'weights': self.metrics[profile['body_shape']]
        }

    def apply(self, garment, body_shape=None, weights=None):
        weight = 0

        # Apply weights based on how distant the garment's body-part emphasis is
        # from the ideal emphasis for a body shape and the importance of having
        # a garment that matches the ideal shape for the wardrobe profile
        for weight_name, field_name in EMPHASIS_FIELDS.items():
            body_part_weight = weights[weight_name]
            ideal_emphasis = body_part_weight['emphasis']
            garment_emphasis = getattr(garment, field_name)
            actual_emphasis_delta = abs(EMPHASIS_RANKS[ideal_emphasis] - EMPHASIS_RANKS[garment_emphasis])

            garment_weight = body_part_weight['importance'] / (actual_emphasis_delta + 1)
            weight += garment_weight

            if self.debug:
                reason = 'A %s %s emphasis is %s for a %s shape and of %s importance' % (
                    EMPHASIS_DISPLAY[garment_emphasis].lower(),
                    weight_name,
                    EMPHASIS_DELTA_STATES[actual_emphasis_delta],
                    body_shape.lower(),
                    IMPORTANCE_DISPLAY[body_part_weight['importance']]
                )
                self.explain_weight(garment, garment_weight, reason)

        # Add bonus weights to the garment if it defines a pant rise that
        # matches one of the ideal rises for the body shape
        pant_reason = None
        pant_weight = IMPORTANCES['LOW']
        if garment.pant_rise and garment.pant_rise in weights['pant_rises']:
            weight += pant_weight
            pant_reason = 'A %s pant rise is flattering for a %s shape' % (garment.pant_rise, body_shape.lower())

        if self.debug and pant_reason:
            self.explain_weight(garment, pant_weight, pant_reason)

        return weight

    def _validate_metrics(self, metrics):
        """Ensure that body-shape metrics are valid.

        Args:
            metrics (dict): Body-shape metrics to use for generating recommendations

        Returns:
            dict: The validated metrics

        Raises:
            chiton.core.exceptions.FormatError: If the metrics are invalid
        """
        known_shapes = set(BODY_SHAPES.values())
        given_shapes = set(metrics.keys())

        invalid_shapes = sorted(list(given_shapes - known_shapes))
        if invalid_shapes:
            raise FormatError('%s is not a known body-shape identifier' % invalid_shapes[0])

        for body_shape, data in metrics.items():
            try:
                METRICS_SCHEMA(data)
            except V.MultipleInvalid as e:
                raise FormatError('Invalid metrics format: %s' % e)

        return metrics
