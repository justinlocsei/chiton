from django.test import TestCase

from chiton.rack.models import AffiliateNetwork


class AffiliateNetworkTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug."""
        network = AffiliateNetwork.objects.create(name="Fancy Pants", slug="fancy_pants")
        self.assertEqual(network.natural_key(), ('fancy_pants',))

        found = AffiliateNetwork.objects.get_by_natural_key('fancy_pants')
        self.assertEqual(network.pk, found.pk)
