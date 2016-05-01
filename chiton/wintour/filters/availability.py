from chiton.wintour.filters import BaseFilter


class AvailabilityFilter(BaseFilter):
    """A filter that excludes unavailable garments."""

    name = 'Availability'
    slug = 'availability'
