from django.core.exceptions import ValidationError
import pytest

from chiton.closet.data import SIZES
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
        size = Size.objects.create(name=SIZES['M'], size_lower=4, size_upper=6, slug="medium")
        assert size.natural_key() == ('medium',)

        found = Size.objects.get_by_natural_key('medium')
        assert size.pk == found.pk

    def test_slug_variant(self):
        """It uses the variant type in the slug."""
        kwargs = {'name': SIZES['M'], 'size_lower': 4, 'size_upper': 6}

        normal = Size.objects.create(**kwargs)
        petite = Size.objects.create(is_petite=True, **kwargs)
        tall = Size.objects.create(is_tall=True, **kwargs)

        assert 'petite' not in normal.slug
        assert 'tall' not in normal.slug

        assert 'petite' in petite.slug
        assert 'tall' not in petite.slug

        assert 'tall' in tall.slug
        assert 'petite' not in tall.slug

    def test_clean_size_range(self):
        """It requires a properly ordered size range."""
        size = Size(name=SIZES['M'])
        size.size_lower = 4
        size.size_upper = 2

        with pytest.raises(ValidationError):
            size.full_clean()

        size.size_upper = 6
        assert size.full_clean() is None

    def test_clean_size_range_partial(self):
        """It only cleans the size when one part of the range is provided."""
        size = Size(name=SIZES['M'])
        assert size.full_clean() is None

        size.size_lower = 4
        with pytest.raises(ValidationError):
            size.full_clean()

        size.size_lower = None
        size.size_upper = 6
        with pytest.raises(ValidationError):
            size.full_clean()

    def test_clean_variants(self):
        """It prevents a size from having multiple variants."""
        size = Size(name=SIZES['M'])
        size.is_tall = True
        size.is_petite = True
        size.is_plus_sized = True

        with pytest.raises(ValidationError):
            size.full_clean()

        size.is_tall = False
        with pytest.raises(ValidationError):
            size.full_clean()

        size.is_plus_sized = False
        assert size.full_clean() is None

    def test_full_name(self):
        """It shows the size name by default."""
        size = Size(name=SIZES['M'])
        assert size.display_name == 'M'

    def test_full_name_range(self):
        """It shows the size range in the full name."""
        size = Size(name=SIZES['M'], size_lower=4, size_upper=6)
        assert size.display_name == 'M (4-6)'

    def test_full_name_single_size(self):
        """It does not show a range for a size with a single numeric size's full name."""
        size = Size(name=SIZES['M'], size_lower=4, size_upper=4)
        assert size.display_name == 'M (4)'

    def test_full_name_tall(self):
        """It uses a prefix for tall sizes."""
        tall = Size(name=SIZES['M'], size_lower=4, size_upper=6, is_tall=True)
        assert tall.display_name == 'Tall M (4-6)'

    def test_full_name_petite(self):
        """It uses a prefix for petite sizes."""
        petite = Size(name=SIZES['M'], size_lower=4, size_upper=6, is_petite=True)
        assert petite.display_name == 'Petite M (4-6)'

    def test_full_name_plus(self):
        """It does not use a variant for plus sizes."""
        plus_normal = Size(name=SIZES['PLUS_1X'], size_lower=18, size_upper=22, is_plus_sized=False)
        plus_variant = Size(name=SIZES['PLUS_1X'], size_lower=18, size_upper=22, is_plus_sized=True)

        assert plus_variant.display_name == 'Plus 1X (18-22)'
        assert plus_normal.display_name == plus_variant.display_name

        assert not plus_normal.is_plus_sized
        assert plus_variant.is_plus_sized
