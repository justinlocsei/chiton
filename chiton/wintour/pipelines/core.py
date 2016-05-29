from chiton.wintour.facets.price import PriceFacet
from chiton.wintour.garment_filters.availability import AvailabilityGarmentFilter
from chiton.wintour.pipelines import BasePipeline
from chiton.wintour.query_filters.formality import FormalityQueryFilter
from chiton.wintour.weights.age import AgeWeight
from chiton.wintour.weights.body_shape import BodyShapeWeight
from chiton.wintour.weights.care import CareWeight
from chiton.wintour.weights.featured import FeaturedWeight
from chiton.wintour.weights.formality import FormalityWeight
from chiton.wintour.weights.style import StyleWeight

from chiton.closet.data import EMPHASES, PANT_RISES
from chiton.wintour.data import BODY_SHAPES, IMPORTANCES


# Metrics for the body-shape weight
BODY_SHAPE_METRICS = {
    BODY_SHAPES['APPLE']: {
        'shoulder': {
            'emphasis': EMPHASES['WEAK'],
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
            'importance': IMPORTANCES['LOW']
        },
        'waist': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'hip': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['LOW']
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
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['MEDIUM']
        },
        'waist': {
            'emphasis': EMPHASES['NEUTRAL'],
            'importance': IMPORTANCES['LOW']
        },
        'hip': {
            'emphasis': EMPHASES['STRONG'],
            'importance': IMPORTANCES['HIGH']
        },
        'pant_rises': (PANT_RISES['LOW'], PANT_RISES['NORMAL'])
    }
}


class CorePipeline(BasePipeline):
    """The core pipeline used for matching."""

    def provide_query_filters(self):
        return [
            FormalityQueryFilter()
        ]

    def provide_garment_filters(self):
        return [
            AvailabilityGarmentFilter()
        ]

    def provide_weights(self):
        return [
            AgeWeight(),
            BodyShapeWeight(importance=2, metrics=BODY_SHAPE_METRICS),
            CareWeight(),
            FeaturedWeight(importance=0.25),
            FormalityWeight(importance=3),
            StyleWeight()
        ]

    def provide_facets(self):
        return [
            PriceFacet()
        ]
