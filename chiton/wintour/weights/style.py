from chiton.wintour.weights import BaseWeight


class StyleWeight(BaseWeight):
    """A weight that gives preference to garments matching a user's styles."""

    name = 'Style'
    slug = 'style'
