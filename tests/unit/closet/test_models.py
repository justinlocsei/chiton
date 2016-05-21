from django.core.exceptions import ValidationError
import pytest

from chiton.closet.models import Brand, Color, Garment, Size


@pytest.mark.django_db
class TestBrand:

    def test_natural_key(self):
        """It uses its slug."""
        brand = Brand.objects.create(name="Chanel", slug="chanel")
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
class TestColor:

    def test_natural_key(self):
        """It uses its slug."""
        color = Color.objects.create(name="Black", slug="black")
        assert color.natural_key() == ('black',)

        found = Color.objects.get_by_natural_key('black')
        assert color.pk == found.pk


@pytest.mark.django_db
class TestGarment:

    def test_natural_key(self, basic_factory):
        """It uses its slug and the slug of its brand."""
        basic = basic_factory()
        brand = Brand.objects.create(name="Givenchy", slug="givenchy")

        garment = Garment.objects.create(name="Cocktail Dress", slug="cocktail-dress", brand=brand, basic=basic)
        assert garment.natural_key() == ('cocktail-dress', 'givenchy')

        found = Garment.objects.get_by_natural_key('cocktail-dress', 'givenchy')
        assert garment.pk == found.pk

    def test_size_validation(self, basic_factory, brand_factory):
        """It requires at least one size to selected."""
        garment = Garment(name="Ball Gown", brand=brand_factory(), basic=basic_factory())

        garment.is_regular_sized = False
        garment.is_plus_sized = False
        garment.is_petite_sized = False
        garment.is_tall_sized = False

        with pytest.raises(ValidationError):
            garment.full_clean()

        garment.is_regular_sized = True
        assert garment.full_clean() is None


@pytest.mark.django_db
class TestSize:

    def test_natural_key(self):
        """It uses its slug."""
        size = Size.objects.create(name='M', slug='m')
        assert size.natural_key() == ('m',)

        found = Size.objects.get_by_natural_key('m')
        assert size.pk == found.pk

    def test_clean_size_range(self):
        """It requires a properly ordered size range."""
        size = Size(name='M')
        size.range_lower = 4
        size.range_upper = 2

        with pytest.raises(ValidationError):
            size.full_clean()

        size.range_upper = 6
        assert size.full_clean() is None

    def test_clean_size_range_partial(self):
        """It only cleans the size when one part of the range is provided."""
        size = Size(name='M')
        assert size.full_clean() is None

        size.range_lower = 4
        with pytest.raises(ValidationError):
            size.full_clean()

        size.range_lower = None
        size.range_upper = 6
        with pytest.raises(ValidationError):
            size.full_clean()
