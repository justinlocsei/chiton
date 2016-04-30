from chiton.wintour.facets import BaseFacet


class PriceFacet(BaseFacet):
    """A facet that groups items by price."""

    def provide_slug(self):
        return 'price'
