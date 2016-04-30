class BaseFacet:
    """The base class for all facets."""

    def provide_slug(self):
        """Provide the slug for the facet.

        Returns:
            str: The facet's slug
        """
        raise NotImplementedError

    @property
    def slug(self):
        """The facet's slug.

        Returns:
            str: The slug
        """
        return self.provide_slug()

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
