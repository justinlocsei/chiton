import pytest

from chiton.closet.models import Garment
from chiton.wintour.query_filters import BaseQueryFilter


class TestFilter(BaseQueryFilter):
    name = 'Test'
    slug = 'test'


@pytest.mark.django_db
class TestBaseQueryFilter:

    def test_apply_default(self, garment_factory):
        """It returns a garment queryset without modifications by default."""
        garment_factory()
        garment_factory()

        query_filter = TestFilter()
        query = Garment.objects.all()
        result = query_filter.apply(query)

        assert query.count() == 2
        assert result.count() == 2
