from chiton.wintour.facets.price import PriceFacet
from chiton.wintour.filters.availability import AvailabilityFilter
from chiton.wintour.filters.formality import FormalityFilter
from chiton.wintour.pipelines import BasePipeline
from chiton.wintour.weights.age import AgeWeight
from chiton.wintour.weights.body_shape import BodyShapeWeight
from chiton.wintour.weights.style import StyleWeight


class CorePipeline(BasePipeline):
    """The core pipeline used for matching."""

    def provide_filters(self):
        return [
            AvailabilityFilter(),
            FormalityFilter()
        ]

    def provide_weights(self):
        return [
            AgeWeight(),
            BodyShapeWeight(),
            StyleWeight(importance=2)
        ]

    def provide_facets(self):
        return [
            PriceFacet()
        ]
