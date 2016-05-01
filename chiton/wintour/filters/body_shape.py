from chiton.wintour.filters import BaseFilter


class BodyShapeFilter(BaseFilter):
    """A filter that excludes garments based on a user's body shape."""

    name = 'Body shape'
    slug = 'body-shape'
