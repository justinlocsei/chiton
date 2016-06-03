import pytest

from chiton.runway import data
from chiton.runway.models import Basic, Category, Formality, Propriety, Style


@pytest.mark.django_db
class TestBasic:

    def test_natural_key(self, category_factory):
        """It uses its slug."""
        basic = Basic.objects.create(name='Cargo Shorts', slug='cargo-shorts', category=category_factory())
        assert basic.natural_key() == ('cargo-shorts',)

        found = Basic.objects.get_by_natural_key('cargo-shorts')
        assert basic.pk == found.pk

    def test_str_name(self):
        """It uses its name for display."""
        basic = Basic.objects.create(name='Jeans')
        assert str(basic) == 'Jeans'


@pytest.mark.django_db
class TestCategory:

    def test_natural_key(self):
        """It uses its slug."""
        category = Category.objects.create(name='Leisure Wear', slug='leisure-wear')
        assert category.natural_key() == ('leisure-wear',)

        found = Category.objects.get_by_natural_key('leisure-wear')
        assert category.pk == found.pk

    def test_str_name(self):
        """It uses its name for display."""
        category = Category.objects.create(name='Pants')
        assert str(category) == 'Pants'


@pytest.mark.django_db
class TestFormality:

    def test_natural_key(self):
        """It uses its slug."""
        formality = Formality.objects.create(name='Snappy Boardroom', slug='snappy-boardroom')
        assert formality.natural_key() == ('snappy-boardroom',)

        found = Formality.objects.get_by_natural_key('snappy-boardroom')
        assert formality.pk == found.pk

    def test_str_name(self):
        """It uses its name for display."""
        formality = Formality.objects.create(name='Executive')
        assert str(formality) == 'Executive'


@pytest.mark.django_db
class TestPropriety:

    def test_natural_key(self, category_factory):
        """It uses the slug of its basic and formality as well as its importance."""
        importance = data.PROPRIETY_IMPORTANCE_CHOICES[0][0]
        basic = Basic.objects.create(name='Cargo Shorts', slug='cargo-shorts', category=category_factory())
        formality = Formality.objects.create(name='Snappy Boardroom', slug='snappy-boardroom')

        propriety = Propriety.objects.create(basic=basic, formality=formality, importance=importance)
        assert propriety.natural_key() == ('cargo-shorts', 'snappy-boardroom', importance)

        found = Propriety.objects.get_by_natural_key('cargo-shorts', 'snappy-boardroom', importance)
        assert propriety.pk == found.pk


@pytest.mark.django_db
class TestStyle:

    def test_natural_key(self):
        """It uses its slug."""
        style = Style.objects.create(name='Nervous, Skittish', slug='nervous-skittish')
        assert style.natural_key() == ('nervous-skittish',)

        found = Style.objects.get_by_natural_key('nervous-skittish')
        assert style.pk == found.pk

    def test_str_name(self):
        """It uses its name for display."""
        style = Style.objects.create(name='Classy')
        assert str(style) == 'Classy'
