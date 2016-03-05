from django.core.exceptions import ValidationError
from django.test import TestCase

from chiton.closet.models import Brand, Formality, Garment, Style


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

    def test_clean_age_range(self):
        """It requires a properly ordered age range."""
        brand = Brand.objects.create(name="Ann Taylor")
        brand.age_lower = 50
        brand.age_upper = 25

        with self.assertRaises(ValidationError):
            brand.full_clean()

        brand.age_upper = 75
        self.assertIsNone(brand.full_clean())


class StyleTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug."""
        style = Style.objects.create(slug="nervous-skittish")
        self.assertEqual(style.natural_key(), ('nervous-skittish',))

        found = Style.objects.get_by_natural_key('nervous-skittish')
        self.assertEqual(style.pk, found.pk)


class FormalityTestCase(TestCase):

    def test_natural_key(self):
        """It uses its slug."""
        formality = Formality.objects.create(slug="snappy-boardroom")
        self.assertEqual(formality.natural_key(), ('snappy-boardroom',))

        found = Formality.objects.get_by_natural_key('snappy-boardroom')
        self.assertEqual(formality.pk, found.pk)
