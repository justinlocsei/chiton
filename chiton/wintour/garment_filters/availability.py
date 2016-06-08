from chiton.rack.models import StockRecord
from chiton.wintour.garment_filters import BaseGarmentFilter


class AvailabilityGarmentFilter(BaseGarmentFilter):
    """A filter that excludes garments that are not offered in any of the user's sizes."""

    name = 'Availability'
    slug = 'availability'

    def provide_profile_data(self, profile):
        available_garments = {}

        # Build a lookup table that maps garment primary keys to arbitrary
        # booleans, with the presence of garments determined by their having at
        # least one available size that matches the user's sizes
        available_garment_ids = (
            StockRecord.objects
            .filter(size__slug__in=profile['sizes'], is_available=True)
            .select_related('item')
            .values_list('item__garment_id', flat=True)
        )
        for garment_id in available_garment_ids:
            available_garments[garment_id] = True

        return {
            'available_garments': available_garments
        }

    def apply(self, garment, available_garments=None):
        return garment.pk not in available_garments
