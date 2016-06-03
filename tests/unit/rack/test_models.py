import pytest

from chiton.rack.models import AffiliateNetwork


@pytest.mark.django_db
class TestAffiliateNetwork:

    def test_natural_key(self):
        """It uses its slug."""
        network = AffiliateNetwork.objects.create(name='Fancy Pants', slug='fancy_pants')
        assert network.natural_key() == ('fancy_pants',)

        found = AffiliateNetwork.objects.get_by_natural_key('fancy_pants')
        assert network.pk == found.pk
