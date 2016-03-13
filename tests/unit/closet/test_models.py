from django.core.exceptions import ValidationError
import pytest

from chiton.closet.models import Brand, Formality, Garment, Style


@pytest.mark.django_db
class TestBrand:

    def test_natural_key(self):
        """It uses its slug."""
        brand = Brand.objects.create(name="Chanel")
        assert brand.natural_key() == ('chanel',)

        found = Brand.objects.get_by_natural_key('chanel')
        assert brand.pk == found.pk

    def test_clean_age_range(self):
        """It requires a properly ordered age range."""
        brand = Brand.objects.create(name="Ann Taylor")
        brand.age_lower = 50
        brand.age_upper = 25

        with pytest.raises(ValidationError):
            brand.full_clean()

        brand.age_upper = 75
        assert brand.full_clean() is None


@pytest.mark.django_db
class TestFormality:

    def test_natural_key(self):
        """It uses its slug."""
        formality = Formality.objects.create(slug="snappy-boardroom")
        assert formality.natural_key() == ('snappy-boardroom',)

        found = Formality.objects.get_by_natural_key('snappy-boardroom')
        assert formality.pk == found.pk


@pytest.mark.django_db
class TestGarment:

    def test_natural_key(self):
        """It uses its slug and the slug of its brand."""
        brand = Brand.objects.create(name="Givenchy")

        garment = Garment.objects.create(name="Cocktail Dress", brand=brand)
        assert garment.natural_key() == ('cocktail-dress', 'givenchy')

        found = Garment.objects.get_by_natural_key('cocktail-dress', 'givenchy')
        assert garment.pk == found.pk


@pytest.mark.django_db
class TestStyle:

    def test_natural_key(self):
        """It uses its slug."""
        style = Style.objects.create(slug="nervous-skittish")
        assert style.natural_key() == ('nervous-skittish',)

        found = Style.objects.get_by_natural_key('nervous-skittish')
        assert style.pk == found.pk
