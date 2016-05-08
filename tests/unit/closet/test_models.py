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


@pytest.mark.django_db
class TestSize:

    def test_natural_key(self):
        """It uses its slug."""
        size = Size.objects.create(base=SIZES['M'], size_lower=4, size_upper=6, slug="medium")
        assert size.natural_key() == ('medium',)

        found = Size.objects.get_by_natural_key('medium')
        assert size.pk == found.pk

    def test_slug_variant(self):
        """It uses the variant type in the slug."""
        kwargs = {'base': SIZES['M'], 'size_lower': 4, 'size_upper': 6}

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
        size = Size(base=SIZES['M'])
        size.size_lower = 4
        size.size_upper = 2

        with pytest.raises(ValidationError):
            size.full_clean()

        size.size_upper = 6
        assert size.full_clean() is None

    def test_clean_tall_petite(self):
        """It prevents a size from being both tall and petite."""
        size = Size(base=SIZES['M'], size_lower=4, size_upper=6)
        size.is_tall = True
        size.is_petite = True

        with pytest.raises(ValidationError):
            size.full_clean()

        size.is_tall = False
        assert size.full_clean() is None

    def test_full_name(self):
        """It shows the size range in the full name."""
        size = Size(base=SIZES['M'], size_lower=4, size_upper=6)
        assert size.full_name == 'M (4-6)'

    def test_full_name_single_size(self):
        """It does not show a range for a size with a single numeric size's full name."""
        size = Size(base=SIZES['M'], size_lower=4, size_upper=4)
        assert size.full_name == 'M (4)'

    def test_full_name_variant(self):
        """It shows the variant as a prefix in the full name."""
        tall = Size(base=SIZES['M'], size_lower=4, size_upper=6, is_tall=True)
        petite = Size(base=SIZES['M'], size_lower=4, size_upper=6, is_petite=True)

        assert tall.full_name == 'Tall M (4-6)'
        assert petite.full_name == 'Petite M (4-6)'
