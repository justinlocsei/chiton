import pytest

from chiton.wintour.facets import BaseFacet


class TestFacet(BaseFacet):
    name = 'Test'
    slug = 'test'


@pytest.mark.django_db
class TestBaseFacet:

    def test_apply_default(self, basic_factory):
        """It returns an empty list of facets by default."""
        basic = basic_factory()

        facet = TestFacet()
        result = facet.apply(basic, [])

        assert result == []
