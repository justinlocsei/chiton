from django.test import TestCase

from chiton.closet.models import Brand, Garment, GarmentCategory


class GarmentTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug and the slug of its brand."""
        brand = Brand.objects.create(name="Givenchy")
        category = GarmentCategory.objects.create(name="Dress")

        garment = Garment.objects.create(name="Cocktail Dress", brand=brand, category=category)
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


class GarmentCategoryTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug."""
        category = GarmentCategory.objects.create(name="Shirt")
        self.assertEqual(category.natural_key(), ('shirt',))

        found = GarmentCategory.objects.get_by_natural_key('shirt')
        self.assertEqual(category.pk, found.pk)
