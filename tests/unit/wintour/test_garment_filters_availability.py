import pytest

from chiton.rack.models import StockRecord
from chiton.wintour.garment_filters.availability import AvailabilityGarmentFilter


@pytest.mark.django_db
class TestAvailabilityGarmentFilter:

    def test_include_available(self, affiliate_item_factory, garment_factory, pipeline_profile_factory, standard_size_factory):
        """It excludes garments that are not available in the user's size."""
        jeans = garment_factory()
        blazer = garment_factory()

        jeans_item = affiliate_item_factory(garment=jeans)
        blazer_item = affiliate_item_factory(garment=blazer)

        small = standard_size_factory(slug='small')
        medium = standard_size_factory(slug='medium')
        large = standard_size_factory(slug='large')

        StockRecord.objects.create(item=jeans_item, size=medium, is_available=True)
        StockRecord.objects.create(item=jeans_item, size=large, is_available=False)

        StockRecord.objects.create(item=blazer_item, size=medium, is_available=False)
        StockRecord.objects.create(item=blazer_item, size=large, is_available=True)

        profile = pipeline_profile_factory(sizes=['small', 'medium'])
        availability_filter = AvailabilityGarmentFilter()

        with availability_filter.apply_to_profile(profile) as filter_fn:
            exclude_jeans = filter_fn(jeans)
            exclude_blazer = filter_fn(blazer)

        assert not exclude_jeans
        assert exclude_blazer
