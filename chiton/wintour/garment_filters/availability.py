from chiton.wintour.garment_filters import BaseGarmentFilter


class AvailabilityGarmentFilter(BaseGarmentFilter):
    """A filter that excludes unavailable garments."""

    name = 'Availability'
    slug = 'availability'
