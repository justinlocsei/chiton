from django.test import TestCase

from chiton.closet.models import Brand, Garment


class GarmentTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug and the slug of its brand."""
        brand = Brand.objects.create(name="Givenchy")

        garment = Garment.objects.create(name="Cocktail Dress", brand=brand)
        self.assertEqual(garment.natural_key(), ('cocktail-dress', 'givenchy'))

        found = Garment.objects.get_by_natural_key('cocktail-dress', 'givenchy')
        self.assertEqual(garment.pk, found.pk)


class BrandTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug."""
        brand = Brand.objects.create(name="Chanel")
        self.assertEqual(brand.natural_key(), ('chanel',))

        found = Brand.objects.get_by_natural_key('chanel')
        self.assertEqual(brand.pk, found.pk)
