from chiton.wintour.pipeline import PipelineStep


class BaseFacet(PipelineStep):
    """The base class for all facets."""

    def apply(self, basic, garments):
        """Apply a facet to a set of garments associated with a basic.

        The facet should return a list of dicts defining each facet grouping,
        with the dict having the following format:

            count (int): The number of items in the group
            garment_ids (list): The IDs of all garments in the group
            slug (str): The slug of the group

        The garments in the provided list will have the following structure:

            affiliate_items (list): A list of AffiliateItem model instances
            garment (chiton.closet.models.Garment): A Garment model instance
            weight (float): The numerical weight for the garment

        Args:
            basic (chiton.runway.models.Basic): The basic type of the given garments
            garments (list): A list of garments exposed as dicts, sorted by weight

        Returns:
            list: A list of dicts defining the facet's groupings
        """
        return []
