from chiton.wintour.pipeline import PipelineStep


class BaseFacet(PipelineStep):
    """The base class for all facets."""

    def apply(self, basic, garments):
        """Apply a facet to a set of garments associated with a basic.

        Args:
            basic (chiton.wintour.pipeline.BasicOverview): The basic type of the given garments
            garments (list[chiton.wintour.pipeline.GarmentRecommendation]): A list of garment recommendations, sorted by weight

        Returns:
            list[chiton.wintour.pipeline.FacetGroup]: A list of facet groups
        """
        return []
