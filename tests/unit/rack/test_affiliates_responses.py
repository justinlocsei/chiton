from decimal import Decimal

import pytest

from chiton.core.exceptions import FormatError
from chiton.rack.affiliates.responses import ItemAvailability, ItemDetails, ItemImage, ItemOverview


class TestItemAvailability:

    def test_valid(self):
        """It accepts a valid availability record."""
        record = ItemAvailability({'size': 8, 'is_regular': True})

        assert record['size'] == 8
        assert record['is_regular']

    def test_invalid_size(self):
        """It requires sizes to be positive integers."""
        with pytest.raises(FormatError):
            ItemAvailability({'size': '8', 'is_regular': True})

        with pytest.raises(FormatError):
            ItemAvailability({'size': -8, 'is_regular': True})

    def test_variant_defaults(self):
        """It ensures that all variants have a boolean default."""
        record = ItemAvailability({'size': 8})

        assert record['is_petite'] is False
        assert record['is_plus_sized'] is False
        assert record['is_regular'] is False
        assert record['is_tall'] is False


class TestItemDetails:

    @pytest.fixture
    def valid_details(self):
        return {
            'availability': True,
            'image': None,
            'name': 'Details',
            'price': Decimal('10.99'),
            'thumbnail': None
        }

    def test_valid(self, valid_details):
        """It accepts a valid details record."""
        details = ItemDetails(valid_details)

        assert details['availability']
        assert details['image'] is None
        assert details['name'] == 'Details'
        assert details['price'] == Decimal('10.99')
        assert details['thumbnail'] is None

    def test_valid_availability(self, valid_details):
        """It can accept item-availability records."""
        valid_details['availability'] = [{'size': 8}]
        details = ItemDetails(valid_details)

        assert details['availability'][0]['size'] == 8

    def test_valid_image(self, valid_details):
        """It can accept image records."""
        image_data = {
            'height': 100,
            'url': 'http://example.com',
            'width': 100
        }

        valid_details['image'] = image_data
        valid_details['thumbnail'] = image_data

        details = ItemDetails(valid_details)

        assert details['image'] == image_data
        assert details['thumbnail'] == image_data

    def test_invalid_name(self, valid_details):
        """It requires a non-empty string for the name."""
        valid_details['name'] = ''

        with pytest.raises(FormatError):
            ItemDetails(valid_details)


class TestItemOverview:

    def test_valid(self):
        """It accepts a valid overview."""
        overview = ItemOverview({
            'guid': '1234',
            'name': 'Item'
        })

        assert overview['guid'] == '1234'
        assert overview['name'] == 'Item'

    def test_invalid_guid(self):
        """It requires a string GUID."""
        with pytest.raises(FormatError):
            ItemOverview({
                'guid': 1234,
                'name': 'Item'
            })

    def test_invalid_name(self):
        """It requires a non-empty string for the name."""
        with pytest.raises(FormatError):
            ItemOverview({
                'guid': '1234',
                'name': ''
            })


class TestItemImage:

    def test_valid(self):
        """It accepts a valid image."""
        image = ItemImage({
            'height': 100,
            'url': 'http://example.com',
            'width': 100
        })

        assert image['height'] == 100
        assert image['url'] == 'http://example.com'
        assert image['width'] == 100

    def test_invalid_url(self):
        """It requires a non-empty string for the URL."""
        with pytest.raises(FormatError):
            ItemImage({
                'height': 100,
                'url': '',
                'width': 100
            })