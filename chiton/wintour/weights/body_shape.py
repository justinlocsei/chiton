from chiton.closet.data import EMPHASES, PANT_RISES
from chiton.wintour.data import BODY_SHAPES
from chiton.wintour.weights import BaseWeight


EMPHASIS_FIELDS = {
    'hip': 'hip_emphasis',
    'shoulder': 'shoulder_emphasis',
    'waist': 'waist_emphasis'
}

EMPHASIS_RANKS = {
    EMPHASES['WEAK']: 0,
    EMPHASES['NEUTRAL']: 1,
    EMPHASES['STRONG']: 2
}

IMPORTANCES = {
    'LOW': 2,
    'MEDIUM': 3,
    'HIGH': 4
}

BODY_SHAPE_WEIGHTS = {
    BODY_SHAPES['APPLE']: {
        'shoulder': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'waist': {
            'emphasis': EMPHASES['WEAK'],
            'importance': IMPORTANCES['HIGH']
        },
        'hip': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'pant_rises': (PANT_RISES['LOW'], PANT_RISES['NORMAL'])
    },
    BODY_SHAPES['HOURGLASS']: {
        'shoulder': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'waist': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['HIGH']
        },
        'hip': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'pant_rises': (PANT_RISES['NORMAL'], PANT_RISES['HIGH'])
    },
    BODY_SHAPES['INVERTED_TRIANGLE']: {
        'shoulder': {
            'emphasis': EMPHASES['WEAK'],
            'importance': IMPORTANCES['HIGH']
        },
        'waist': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['LOW']
        },
        'hip': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'pant_rises': (PANT_RISES['LOW'], PANT_RISES['NORMAL'])
    },
    BODY_SHAPES['PEAR']: {
        'shoulder': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'waist': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['LOW']
        },
        'hip': {
            'emphasis': EMPHASES['WEAK'],
            'importance': IMPORTANCES['HIGH']
        },
        'pant_rises': (PANT_RISES['NORMAL'], PANT_RISES['HIGH'])
    },
    BODY_SHAPES['RECTANGLE']: {
        'shoulder': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'waist': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'hip': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['HIGH']
        },
        'pant_rises': (PANT_RISES['LOW'], PANT_RISES['NORMAL'])
    }
}


class BodyShapeWeight(BaseWeight):
    """A weight that compares a user's body shape with a garment's cut."""

    name = 'Body shape'
    slug = 'body-shape'

    def provide_profile_data(self, profile):
        return {
            'weights': BODY_SHAPE_WEIGHTS[profile.body_shape]
        }

    def apply(self, garment, weights=None):
        weight = 0

        # Apply weights based on how distant the garment's body-part emphasis is
        # from the ideal emphasis for a body shape and the importance of having
        # a garment that matches the ideal shape for the wardrobe profile
        for weight_name, field_name in EMPHASIS_FIELDS.items():
            field_weight = weights[weight_name]
            ideal_emphasis = field_weight['emphasis']
            garment_emphasis = getattr(garment, field_name)
            actual_emphasis_delta = abs(EMPHASIS_RANKS[ideal_emphasis] - EMPHASIS_RANKS[garment_emphasis])

            garment_weight = field_weight['importance'] / (actual_emphasis_delta + 1)
            weight += garment_weight

        # Add bonus weights to the garment if it defines a pant rise that
        # matches one of the ideal rises for the wardrobe profile
        if garment.pant_rise and garment.pant_rise in weights['pant_rises']:
            weight += IMPORTANCES['LOW']

        return weight
