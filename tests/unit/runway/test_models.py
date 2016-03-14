import pytest

from chiton.runway.models import Basic, Category, Formality, Propriety, Style


@pytest.mark.django_db
class TestBasic:

    def test_natural_key(self):
        """It uses its slug."""
        category = Category.objects.create(name="Leisure wear")
        basic = Basic.objects.create(slug="cargo-shorts", category=category)
        assert basic.natural_key() == ('cargo-shorts',)

        found = Basic.objects.get_by_natural_key('cargo-shorts')
        assert basic.pk == found.pk


@pytest.mark.django_db
class TestCategory:

    def test_natural_key(self):
        """It uses its slug."""
        category = Category.objects.create(slug="leisure-wear")
        assert category.natural_key() == ('leisure-wear',)

        found = Category.objects.get_by_natural_key('leisure-wear')
        assert category.pk == found.pk


@pytest.mark.django_db
class TestFormality:

    def test_natural_key(self):
        """It uses its slug."""
        formality = Formality.objects.create(slug="snappy-boardroom")
        assert formality.natural_key() == ('snappy-boardroom',)

        found = Formality.objects.get_by_natural_key('snappy-boardroom')
        assert formality.pk == found.pk


@pytest.mark.django_db
class TestPropriety:

    def test_natural_key(self):
        """It uses the slug of its basic and formality as well as its weight."""
        category = Category.objects.create(name="Leisure wear")
        basic = Basic.objects.create(slug="cargo-shorts", category=category)
        formality = Formality.objects.create(slug="snappy-boardroom")

        propriety = Propriety.objects.create(basic=basic, formality=formality, weight=1)
        assert propriety.natural_key() == ('cargo-shorts', 'snappy-boardroom', 1)

        found = Propriety.objects.get_by_natural_key('cargo-shorts', 'snappy-boardroom', 1)
        assert propriety.pk == found.pk


@pytest.mark.django_db
class TestStyle:

    def test_natural_key(self):
        """It uses its slug."""
        style = Style.objects.create(slug="nervous-skittish")
        assert style.natural_key() == ('nervous-skittish',)

        found = Style.objects.get_by_natural_key('nervous-skittish')
        assert style.pk == found.pk
