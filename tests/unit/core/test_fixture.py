import json
import tempfile

import mock
import pytest

from chiton.core.exceptions import FilesystemError
from chiton.core.fixture import Fixture
from chiton.rack.models import ItemImage


@pytest.mark.django_db
class TestFixture:

    @pytest.fixture
    def item_images_fixture(self, item_image_factory):
        item_image_factory()
        item_images = ItemImage.objects.all()

        return Fixture(ItemImage, item_images)

    def test_label(self, item_images_fixture):
        """It creates a label using the underscored version of its model's name."""
        assert item_images_fixture.label == 'item_image'

    def test_find(self, item_images_fixture, settings):
        """It returns the absolute path to the fixture's file using the app label and fixture label."""
        settings.CHITON_ROOT = '/tmp'

        path = item_images_fixture.find()
        assert path == '/tmp/rack/fixtures/item_image.json'

    def test_is_needed(self, item_images_fixture):
        """It reports fixtures as needed by defaut."""
        assert item_images_fixture.is_needed()

    def test_is_needed_initial(self, item_image_factory):
        """It reports an initial fixture as unneeded if it has models."""
        fixture = Fixture(ItemImage, initial=True)
        assert fixture.is_needed()

        item_image_factory()
        assert not fixture.is_needed()

    def test_is_needed_initial_queryset(self, item_image_factory):
        """It reports an initial fixture as needed if its queryset does not exist."""
        fixture = Fixture(ItemImage, queryset=ItemImage.objects.filter(height=100), initial=True)

        item_image_factory(height=50)
        assert fixture.is_needed()

        item_image_factory(height=100)
        assert not fixture.is_needed()

    def test_export(self, item_images_fixture):
        """It writes a queryset's models to a JSON file."""
        with tempfile.NamedTemporaryFile() as output:
            item_images_fixture.find = mock.Mock(return_value=output.name)

            exported = item_images_fixture.export()
            assert exported == output.name

            with open(exported) as fixture_file:
                data = json.load(fixture_file)

            assert len(data) == 1

            image = data[0]
            assert 'fields' in image
            assert 'model' in image
            assert 'pk' in image

    def test_export_fields(self):
        """It can accept a subset of fields to serialize."""
        ItemImage.objects.create(url='http://example.com', height=50, width=50)
        fixture = Fixture(ItemImage, fields=['url', 'height'])

        with tempfile.NamedTemporaryFile() as output:
            fixture.find = mock.Mock(return_value=output.name)

            exported = fixture.export()
            assert exported == output.name

            with open(exported) as fixture_file:
                data = json.load(fixture_file)

            fields = data[0]['fields']
            assert 'height' in fields
            assert 'url' in fields
            assert 'width' not in fields

    def test_export_invalid_target(self, item_images_fixture):
        """It raises an error when the target directory does not exist."""
        item_images_fixture.find = mock.Mock(return_value='/abcdefghijklmnop/qrstuvwxyz.json')

        with pytest.raises(FilesystemError):
            item_images_fixture.export()
