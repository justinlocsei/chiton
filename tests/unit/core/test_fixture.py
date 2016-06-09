import json
import tempfile

import mock
import pytest

from chiton.core.exceptions import FilesystemError
from chiton.core.fixture import Fixture
from chiton.rack.models import ProductImage


@pytest.mark.django_db
class TestFixture:

    @pytest.fixture
    def product_images_fixture(self, product_image_factory):
        product_image_factory()
        product_images = ProductImage.objects.all()

        return Fixture(ProductImage, product_images)

    def test_label(self, product_images_fixture):
        """It creates a label using the underscored version of its model's name."""
        assert product_images_fixture.label == 'product_image'

    def test_find(self, product_images_fixture, settings):
        """It returns the absolute path to the fixture's file using the app label and fixture label."""
        settings.CHITON_ROOT = '/tmp'

        path = product_images_fixture.find()
        assert path == '/tmp/rack/fixtures/product_image.json'

    def test_export(self, product_images_fixture):
        """It writes a queryset's models to a JSON file."""
        with tempfile.NamedTemporaryFile() as output:
            product_images_fixture.find = mock.Mock(return_value=output.name)

            exported = product_images_fixture.export()
            assert exported == output.name

            with open(exported) as fixture_file:
                data = json.load(fixture_file)

            assert len(data) == 1

            image = data[0]
            assert 'fields' in image
            assert 'model' in image
            assert 'pk' in image

    def test_export_invalid_target(self, product_images_fixture):
        """It raises an error when the target directory does not exist."""
        product_images_fixture.find = mock.Mock(return_value='/abcdefghijklmnop/qrstuvwxyz.json')

        with pytest.raises(FilesystemError):
            product_images_fixture.export()
