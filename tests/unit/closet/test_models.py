from django.core.exceptions import ValidationError
import pytest

from chiton.closet.models import Brand, CanonicalSize, Color, Garment, StandardSize


@pytest.mark.django_db
class TestBrand:

    def test_natural_key(self):
        """It uses its slug."""
        brand = Brand.objects.create(name='Chanel', slug='chanel', age_lower=20, age_upper=30)
        assert brand.natural_key() == ('chanel',)

        found = Brand.objects.get_by_natural_key('chanel')
        assert brand.pk == found.pk

    def test_clean_age_range(self):
        """It requires a properly ordered age range."""
        brand = Brand(name='Ann Taylor')
        brand.age_lower = 50
        brand.age_upper = 25

        with pytest.raises(ValidationError):
            brand.full_clean()

        brand.age_upper = 75
        assert brand.full_clean() is None

    def test_str_name(self):
        """It uses its name for display."""
        brand = Brand.objects.create(name='Armani', age_lower=20, age_upper=40)
        assert str(brand) == 'Armani'


@pytest.mark.django_db
class TestColor:

    def test_natural_key(self):
        """It uses its slug."""
        color = Color.objects.create(name='Black', slug='black')
        assert color.natural_key() == ('black',)

        found = Color.objects.get_by_natural_key('black')
        assert color.pk == found.pk

    def test_str_name(self):
        """It uses its name for display."""
        color = Color.objects.create(name='Blue')
        assert str(color) == 'Blue'


@pytest.mark.django_db
class TestGarment:

    def test_natural_key(self, basic_factory, brand_factory):
        """It uses its slug and the slug of its brand."""
        basic = basic_factory()
        brand = brand_factory(name='Givenchy', slug='givenchy')

        garment = Garment.objects.create(name='Cocktail Dress', slug='cocktail-dress', brand=brand, basic=basic)
        assert garment.natural_key() == ('cocktail-dress', 'givenchy')

        found = Garment.objects.get_by_natural_key('cocktail-dress', 'givenchy')
        assert garment.pk == found.pk

    def test_size_validation(self, basic_factory, brand_factory):
        """It requires at least one size to selected."""
        garment = Garment(name='Ball Gown', brand=brand_factory(), basic=basic_factory())

        garment.is_regular_sized = False
        garment.is_plus_sized = False
        garment.is_petite_sized = False
        garment.is_tall_sized = False

        with pytest.raises(ValidationError):
            garment.full_clean()

        garment.is_regular_sized = True
        assert garment.full_clean() is None

    def test_str_name(self, basic_factory, brand_factory):
        """It uses its name for display."""
        garment = Garment(name='Blazer', brand=brand_factory(), basic=basic_factory())
        assert str(garment) == 'Blazer'


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

    def test_str_name(self):
        """It uses its name for display."""
        size = CanonicalSize(name='L')
        assert str(size) == 'L'


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
        m_plus = StandardSize.objects.create(canonical=canonical, is_plus_sized=True)

        assert m_regular.slug == 'm'
        assert m_petite.slug == 'm-petite'
        assert m_tall.slug == 'm-tall'
        assert m_plus.slug == 'm-plus'

    def test_display_name(self, canonical_size_factory):
        """It shows the size variant as a prefix of the canonical name."""
        xl = canonical_size_factory(name='XL', range_lower=10, range_upper=10)
        x2 = canonical_size_factory(name='2X', range_lower=16, range_upper=18)

        xl_regular = StandardSize.objects.create(canonical=xl)
        xl_petite = StandardSize.objects.create(canonical=xl, is_petite=True)
        xl_tall = StandardSize.objects.create(canonical=xl, is_tall=True)
        plus_2x = StandardSize.objects.create(canonical=x2, is_plus_sized=True)

        assert xl_regular.display_name == 'XL (10)'
        assert xl_petite.display_name == 'Petite XL (10)'
        assert xl_tall.display_name == 'Tall XL (10)'
        assert plus_2x.display_name == 'Plus 2X (16-18)'

    def test_validation_variants(self, canonical_size_factory):
        """It ensure that only one variant is selected."""
        canonical = canonical_size_factory()
        size = StandardSize(canonical=canonical)

        with pytest.raises(ValidationError):
            size.is_regular = False
            size.full_clean()

        with pytest.raises(ValidationError):
            size.is_regular = True
            size.is_tall = True
            size.full_clean()

        size.is_tall = False
        assert size.full_clean() is None

    def test_str_display_name(self, canonical_size_factory):
        """It uses its display name for display."""
        m = canonical_size_factory(name='M', range_lower=6, range_upper=8)
        m_regular = StandardSize.objects.create(canonical=m)

        assert str(m_regular) == 'M (6-8)'

    def test_get_slugs(self, standard_size_factory):
        """It produces an ordered list of size slugs."""
        standard_size_factory(slug='beta')
        standard_size_factory(slug='alpha')
        standard_size_factory(slug='gamma')

        assert StandardSize.objects.get_slugs() == ['alpha', 'beta', 'gamma']

    def test_get_slugs_update(self, standard_size_factory):
        """It updates the list of slugs when standard sizes change."""
        standard_size_factory(slug='alpha')
        assert StandardSize.objects.get_slugs() == ['alpha']

        standard_size_factory(slug='beta')
        assert StandardSize.objects.get_slugs() == ['alpha', 'beta']
