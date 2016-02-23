from django.test import TestCase

from chiton.closet.models import Brand, Line, Garment, GarmentCategory


def create_brand(name):
    return Brand.objects.create(name=name)


def create_line(brand):
    return Line.objects.create(name=brand.name, brand=brand)


def create_category(name):
    return GarmentCategory.objects.create(name=name)


class GarmentTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug and the slug of its line."""
        brand = create_brand("Givenchy")
        category = create_category("Dress")

        garment = Garment.objects.create(name="Cocktail Dress", line=create_line(brand), category=category)
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


class LineTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug and the slug of its brand."""
        brand = Brand.objects.create(name="Lands' End")

        line = Line.objects.create(name="Starfish", brand=brand)
        self.assertEqual(line.natural_key(), ('starfish', 'lands-end'))

        found = Line.objects.get_by_natural_key('starfish', 'lands-end')
        self.assertEqual(line.pk, found.pk)


class GarmentCategoryTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug."""
        category = GarmentCategory.objects.create(name="Shirt")
        self.assertEqual(category.natural_key(), ('shirt',))

        found = GarmentCategory.objects.get_by_natural_key('shirt')
        self.assertEqual(category.pk, found.pk)
