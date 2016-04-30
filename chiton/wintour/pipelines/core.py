from chiton.wintour.facets.price import PriceFacet
from chiton.wintour.filters.availability import AvailabilityFilter
from chiton.wintour.filters.basic import BasicFilter
from chiton.wintour.filters.body_shape import BodyShapeFilter
from chiton.wintour.filters.formality import FormalityFilter
from chiton.wintour.pipelines import BasePipeline, PipelineWeight
from chiton.wintour.weights.age import AgeWeight
from chiton.wintour.weights.body_shape import BodyShapeWeight
from chiton.wintour.weights.bust import BustWeight
from chiton.wintour.weights.pant_rise import PantRiseWeight
from chiton.wintour.weights.style import StyleWeight


class CorePipeline(BasePipeline):
    """The core pipeline used for matching."""

    def provide_filters(self):
        return [
            AvailabilityFilter,
            BasicFilter,
            BodyShapeFilter,
            FormalityFilter
        ]

    def provide_weights(self):
        return [
            PipelineWeight(AgeWeight),
            PipelineWeight(BodyShapeWeight),
            PipelineWeight(BustWeight),
            PipelineWeight(PantRiseWeight),
            PipelineWeight(StyleWeight, importance=2)
        ]

    def provide_facets(self):
        return [
            PriceFacet
        ]
