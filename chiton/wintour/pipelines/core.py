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
            BodyShapeWeight(importance=2),
            CareWeight(),
            FeaturedWeight(importance=0.25),
            FormalityWeight(importance=2),
            StyleWeight()
        ]

    def provide_facets(self):
        return [
            PriceFacet()
        ]
