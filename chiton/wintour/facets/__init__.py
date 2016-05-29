from chiton.wintour.pipeline import PipelineStep


class BaseFacet(PipelineStep):
    """The base class for all facets."""

    def apply(self, basic, garments):
        """Apply a facet to a set of garments associated with a basic.

        The facet should return a list of dicts defining each facet grouping,
        with the dict having the following format:

            count - The number of items in the group
            items - The IDs of all garments in the group
            slug  - The slug of the group

        Args:
            basic (chiton.runway.models.Basic): The basic type of the given garments
            garments (list): A list of garments exposed as dicts, sorted by weight

        Returns:
            list: A list of dicts defining the facet's groupings
        """
        return []
