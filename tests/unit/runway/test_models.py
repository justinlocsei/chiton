import pytest

from chiton.runway.models import Formality, Style


@pytest.mark.django_db
class TestFormality:

    def test_natural_key(self):
        """It uses its slug."""
        formality = Formality.objects.create(slug="snappy-boardroom")
        assert formality.natural_key() == ('snappy-boardroom',)

        found = Formality.objects.get_by_natural_key('snappy-boardroom')
        assert formality.pk == found.pk


@pytest.mark.django_db
class TestStyle:

    def test_natural_key(self):
        """It uses its slug."""
        style = Style.objects.create(slug="nervous-skittish")
        assert style.natural_key() == ('nervous-skittish',)

        found = Style.objects.get_by_natural_key('nervous-skittish')
        assert style.pk == found.pk
