from decimal import Decimal

import mock
import pytest

from chiton.closet.models import Color, Size
from chiton.rack.affiliates.data import update_affiliate_item_details, update_affiliate_item_metadata
from chiton.rack.affiliates.base import Affiliate


CREATE_AFFILIATE = 'chiton.rack.affiliates.data.create_affiliate'


class FullAffiliate(Affiliate):
    """An affiliate that returns full API information."""

    def provide_overview(self, url):
        return {
            'name': 'Test Name',
            'guid': '1234'
        }

    def provide_details(self, guid, colors=[]):
        return {
            'availability': [
                {'size': 'Large'},
                {'size': 'Jumbo'}
            ],
            'image': {
                'height': 100,
                'url': 'http://example.com/%s' % '/'.join(colors),
                'width': 100
            },
            'price': Decimal('9.99'),
            'thumbnail': {
                'height': 50,
                'url': 'http://example.net/%s' % guid,
                'width': 50
            }
        }


class OutOfStockAffiliate(Affiliate):
    """An affiliate that indicates that an item is out-of-stock."""

    def provide_details(self, guid, colors=[]):
        return {
            'availability': False,
            'image': {
                'height': 100,
                'url': 'http://example.com/image',
                'width': 100
            },
            'price': Decimal('9.99'),
            'thumbnail': {
                'height': 50,
                'url': 'http://example.com/thumbnail',
                'width': 50
            }
        }


class InStockAffiliate(OutOfStockAffiliate):
    """An affiliate that indicates that all sizes are available."""

    def provide_details(self, guid, colors=[]):
        details = super().provide_details(guid, colors)
        details['availability'] = True
        return details


@pytest.fixture
def affiliate_item(basic_factory, garment_factory, affiliate_item_factory):
    white = Color.objects.create(name='White')
    gray = Color.objects.create(name='Gray')
    blue = Color.objects.create(name='Blue')

    basic = basic_factory(primary_color=white)
    basic.secondary_colors.add(gray)
    basic.secondary_colors.add(blue)
    garment = garment_factory(basic=basic)

    return affiliate_item_factory(garment=garment)


@pytest.mark.django_db
class TestUpdateAffiliateItemMetadata:

    def test_affiliate_network(self, affiliate_network_factory, affiliate_item_factory):
        """It creates an affiliate instance using the item's network slug."""
        network = affiliate_network_factory(slug='shopping')
        affiliate_item = affiliate_item_factory(network=network)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_metadata(affiliate_item)

            create_affiliate.assert_called_with(slug='shopping')

    def test_update_data(self, affiliate_item):
        """It re-fetches the item's GUID and name."""
        affiliate_item.guid = '4321'
        affiliate_item.name = 'Changed'
        affiliate_item.save()

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_metadata(affiliate_item)

        assert affiliate_item.guid == '1234'
        assert affiliate_item.name == 'Test Name'


@pytest.mark.django_db
class TestUpdateAffiliateItemDetails:

    def test_affiliate_network(self, affiliate_network_factory, affiliate_item_factory):
        """It creates an affiliate instance using the item's network slug."""
        network = affiliate_network_factory(slug='shopping')
        affiliate_item = affiliate_item_factory(network=network)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

            create_affiliate.assert_called_with(slug='shopping')

    def test_network_data(self, affiliate_item):
        """It adds detailed data to an affiliate item from the affiliate network's API."""
        assert affiliate_item.price is None
        assert affiliate_item.image is None
        assert affiliate_item.thumbnail is None

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

        assert affiliate_item.price == Decimal('9.99')
        assert affiliate_item.image.height == 100
        assert affiliate_item.thumbnail.height == 50

    def test_network_data_guid(self, affiliate_item_factory):
        """It creates an affiliate instance using the item's network slug."""
        affiliate_item = affiliate_item_factory(guid='4321')

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

        assert affiliate_item.thumbnail.url == 'http://example.net/4321'

    def test_network_data_colors(self, affiliate_item):
        """It fetches details using the basic's primary and secondary colors, ordered by name."""
        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

        assert affiliate_item.image.url == 'http://example.com/White/Blue/Gray'

    def test_network_data_colors_empty(self, affiliate_item_factory):
        """It fetches details when no colors are associated with the basic."""
        affiliate_item = affiliate_item_factory()

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

        assert affiliate_item.image.url == 'http://example.com/'

    def test_network_data_images_idempotent(self, affiliate_item):
        """It creates or updates images for the colors."""
        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()

            update_affiliate_item_details(affiliate_item)
            first_image_pk = affiliate_item.image.pk
            first_thumbnail_pk = affiliate_item.thumbnail.pk

            affiliate_item.image.height = 200
            affiliate_item.image.save()

            affiliate_item.thumbnail.height = 100
            affiliate_item.thumbnail.save()

            update_affiliate_item_details(affiliate_item)
            second_image_pk = affiliate_item.image.pk
            second_thumbnail_pk = affiliate_item.thumbnail.pk

        assert first_image_pk is not None
        assert first_thumbnail_pk is not None

        assert first_image_pk == second_image_pk
        assert first_thumbnail_pk == second_thumbnail_pk

        assert affiliate_item.image.height == 100
        assert affiliate_item.thumbnail.height == 50

    def test_network_data_stock_records(self, affiliate_item):
        """It creates stock records for all sizes that match a known size's full display name."""
        Size.objects.create(name='Medium')
        Size.objects.create(name='Large')

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

        availability_by_name = {}
        for record in affiliate_item.stock_records.all():
            availability_by_name[record.size.display_name] = record.is_available

        assert availability_by_name['Large']
        assert not availability_by_name['Medium']
        assert 'Jumbo (10)' not in availability_by_name

    def test_network_data_stock_records_in_stock(self, affiliate_item):
        """It creates in-stock records for all known sizes if an affiliate signals that an item is globally available."""
        Size.objects.create(name='Small')
        Size.objects.create(name='Medium')

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = InStockAffiliate()
            update_affiliate_item_details(affiliate_item)

        records = affiliate_item.stock_records.all()
        assert len(records) == 2
        assert all([r.is_available for r in records])

    def test_network_data_stock_records_out_of_stock(self, affiliate_item):
        """It creates unavailable in-stock records for all known sizes if an affiliate signals that an item is globally unavailable."""
        Size.objects.create(name='Small')
        Size.objects.create(name='Medium')

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = OutOfStockAffiliate()
            update_affiliate_item_details(affiliate_item)

        records = affiliate_item.stock_records.all()
        assert len(records) == 2
        assert not any([r.is_available for r in records])

    def test_network_data_stock_records_existing(self, affiliate_item):
        """It updates stock records for items with existing records."""
        Size.objects.create(name='Medium')

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = InStockAffiliate()

            update_affiliate_item_details(affiliate_item)
            records = affiliate_item.stock_records.all()

            assert len(records) == 1
            medium = records[0]
            create_medium_pk = medium.pk

            medium.is_available = False
            medium.save()

            update_affiliate_item_details(affiliate_item)
            records = affiliate_item.stock_records.all()

            assert len(records) == 1
            medium = records[0]
            update_medium_pk = medium.pk

        assert create_medium_pk is not None
        assert create_medium_pk == update_medium_pk

        assert medium.is_available
