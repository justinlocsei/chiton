import pytest

from chiton.rack.models import AffiliateNetwork


@pytest.mark.django_db
class TestAffiliateItem:

    def test_str_name(self, affiliate_item_factory):
        """It uses its name for display."""
        item = affiliate_item_factory(name='Blazer')
        assert str(item) == 'Blazer'


@pytest.mark.django_db
class TestAffiliateNetwork:

    def test_natural_key(self):
        """It uses its slug."""
        network = AffiliateNetwork.objects.create(name='Fancy Pants', slug='fancy_pants')
        assert network.natural_key() == ('fancy_pants',)

        found = AffiliateNetwork.objects.get_by_natural_key('fancy_pants')
        assert network.pk == found.pk

    def test_str_name(self):
        """It uses its name for display."""
        network = AffiliateNetwork.objects.create(name='Network')
        assert str(network) == 'Network'


@pytest.mark.django_db
class TestItemImage:

    def test_str_dimensions(self, item_image_factory):
        """It uses its dimensions for display."""
        image = item_image_factory(height=20, width=10)
        assert str(image) == '10x20'
