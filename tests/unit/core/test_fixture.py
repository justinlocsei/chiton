import json
import tempfile

import mock
import pytest

from chiton.core.exceptions import FilesystemError
from chiton.core.fixture import Fixture
from chiton.runway.models import Style


@pytest.mark.django_db
class TestFixture:

    @pytest.fixture
    def styles_fixture(self, style_factory):
        style_factory()
        styles = Style.objects.all()

        return Fixture(Style, styles)

    def test_label(self, styles_fixture):
        """It creates a label using from the model's name."""
        assert styles_fixture.label == 'style'

    def test_find(self, styles_fixture, settings):
        """It returns the absolute path to the fixture's file using the app label and fixture label."""
        settings.CHITON_ROOT = '/tmp'

        path = styles_fixture.find()
        assert path == '/tmp/runway/fixtures/style.json'

    def test_is_needed(self, styles_fixture):
        """It reports fixtures as needed by defaut."""
        assert styles_fixture.is_needed()

    def test_is_needed_initial(self, style_factory):
        """It reports an initial fixture as unneeded if it has models."""
        fixture = Fixture(Style, initial=True)
        assert fixture.is_needed()

        style_factory()
        assert not fixture.is_needed()

    def test_is_needed_initial_queryset(self, style_factory):
        """It reports an initial fixture as needed if its queryset does not exist."""
        fixture = Fixture(Style, queryset=Style.objects.filter(name='Classy'), initial=True)

        style_factory(name='Sassy')
        assert fixture.is_needed()

        style_factory(name='Classy')
        assert not fixture.is_needed()

    def test_export(self, styles_fixture):
        """It writes a queryset's models to a JSON file."""
        with tempfile.NamedTemporaryFile() as output:
            styles_fixture.find = mock.Mock(return_value=output.name)

            exported = styles_fixture.export()
            assert exported == output.name

            with open(exported) as fixture_file:
                data = json.load(fixture_file)

            assert len(data) == 1

            style = data[0]
            assert 'fields' in style
            assert 'model' in style

    def test_export_fields(self):
        """It can accept a subset of fields to serialize."""
        Style.objects.create(name='Classy', slug='classy')
        fixture = Fixture(Style, fields=['name'])

        with tempfile.NamedTemporaryFile() as output:
            fixture.find = mock.Mock(return_value=output.name)

            exported = fixture.export()
            assert exported == output.name

            with open(exported) as fixture_file:
                data = json.load(fixture_file)

            fields = list(data[0]['fields'].keys())
            assert fields == ['name']

    def test_export_invalid_target(self, styles_fixture):
        """It raises an error when the target directory does not exist."""
        styles_fixture.find = mock.Mock(return_value='/abcdefghijklmnop/qrstuvwxyz.json')

        with pytest.raises(FilesystemError):
            styles_fixture.export()
