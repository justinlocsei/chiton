from django.core.exceptions import ValidationError
import pytest

from chiton.closet.models import Brand, CanonicalSize, Color, Garment, StandardSize


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
class TestCanonicalSize:

    def test_natural_key(self):
        """It uses its slug."""
        size = CanonicalSize.objects.create(name='M', slug='m', range_lower=6, range_upper=8)
        assert size.natural_key() == ('m',)

        found = CanonicalSize.objects.get_by_natural_key('m')
        assert size.pk == found.pk

    def test_clean_size_range(self):
        """It requires a properly ordered size range."""
        size = CanonicalSize(name='M')
        size.range_lower = 4
        size.range_upper = 2

        with pytest.raises(ValidationError):
            size.full_clean()

        size.range_upper = 6
        assert size.full_clean() is None

    def test_range_display(self):
        """It shows plus sizes as women's sizes."""
        xl = CanonicalSize.objects.create(name='XL', range_lower=14, range_upper=16)
        xl_plus = CanonicalSize.objects.create(name='Plus 1X', range_lower=14, range_upper=16, is_plus_sized=True)

        assert xl.range_lower == 14
        assert xl.range_upper == 16
        assert xl.range_lower_display == '14'
        assert xl.range_upper_display == '16'

        assert xl_plus.range_lower == 14
        assert xl_plus.range_upper == 16
        assert xl_plus.range_lower_display == '14W'
        assert xl_plus.range_upper_display == '16W'


@pytest.mark.django_db
class TestStandardSize:

    def test_natural_key(self, canonical_size_factory):
        """It uses its slug."""
        canonical = canonical_size_factory()
        size = StandardSize.objects.create(canonical=canonical, slug='size')
        assert size.natural_key() == ('size',)

        found = StandardSize.objects.get_by_natural_key('size')
        assert size.pk == found.pk

    def test_slug_variant(self, canonical_size_factory):
        """It uses variants to distinguish size slugs."""
        canonical = canonical_size_factory(slug='m')

        m_regular = StandardSize.objects.create(canonical=canonical)
        m_petite = StandardSize.objects.create(canonical=canonical, is_petite=True)
        m_tall = StandardSize.objects.create(canonical=canonical, is_tall=True)

        assert m_regular.slug == 'm'
        assert m_petite.slug == 'm-petite'
        assert m_tall.slug == 'm-tall'

    def test_display_name(self, canonical_size_factory):
        """It shows the size variant as a prefix of the canonical name."""
        canonical = canonical_size_factory(name='XL')

        xl_regular = StandardSize.objects.create(canonical=canonical)
        xl_petite = StandardSize.objects.create(canonical=canonical, is_petite=True)
        xl_tall = StandardSize.objects.create(canonical=canonical, is_tall=True)

        assert xl_regular.display_name == 'Regular XL'
        assert xl_petite.display_name == 'Petite XL'
        assert xl_tall.display_name == 'Tall XL'
