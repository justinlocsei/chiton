import pytest

from chiton.wintour.garment_filters import BaseGarmentFilter


class DummyFilter(BaseGarmentFilter):
    name = 'Test'
    slug = 'test'


@pytest.mark.django_db
class TestBaseGarmentFilter:

    def test_apply_default(self, garment_factory):
        """It marks a garment as non-excluded by default."""
        garment = garment_factory()

        garment_filter = DummyFilter()
        result = garment_filter.apply(garment)

        assert result is False
