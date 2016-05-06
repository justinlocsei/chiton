from chiton.wintour.pipeline import PipelineStep


class BaseFacet(PipelineStep):
    """The base class for all facets."""

    def apply(self, garments):
        """Apply a facet to a set of garments.

        The facet should be returned as a list of dicts, each of which defines
        the name of the facet and the garments available.

        Args:
            garments (list): A list of garments, sorted by weight

        Returns:
            list: A list of dicts defining the facets
        """
        return []
