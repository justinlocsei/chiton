from decimal import Decimal

import mock
import pytest

from chiton.closet.models import Color
from chiton.rack.affiliates.data import update_affiliate_item_details, update_affiliate_item_metadata
from chiton.rack.affiliates.base import Affiliate
from chiton.rack.models import ProductImage


CREATE_AFFILIATE = 'chiton.rack.affiliates.data.create_affiliate'


class FullAffiliate(Affiliate):
    """An affiliate that returns full API information."""

    availability = []

    def provide_overview(self, url):
        return {
            'name': 'Overview',
            'guid': '1234'
        }

    def provide_details(self, guid, colors=[]):
        if hasattr(self, 'custom_thumbnail'):
            thumbnail = self.custom_thumbnail
        else:
            thumbnail = {
                'height': 50,
                'url': 'http://example.net/%s' % guid,
                'width': 50
            }

        return {
            'availability': self.availability,
            'image': {
                'height': 100,
                'url': 'http://example.com/%s' % '/'.join(colors),
                'width': 100
            },
            'name': 'Details',
            'price': Decimal('9.99'),
            'thumbnail': thumbnail
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
            'name': 'Item',
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
        assert affiliate_item.name == 'Overview'


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

    def test_network_data_name(self, affiliate_item):
        """It updates the item's name if it differs from the stored name."""
        affiliate_item.name = 'Previous'
        affiliate_item.save()

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

        assert affiliate_item.name == 'Details'

    def test_network_data_guid(self, affiliate_item_factory):
        """It uses the item's GUID to perform the API lookup."""
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

    def test_network_data_images_clearing(self, affiliate_item):
        """It removes existing images if a subsequent details request defines no image."""
        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = FullAffiliate()
            update_affiliate_item_details(affiliate_item)

            assert affiliate_item.thumbnail
            thumbnail_pk = affiliate_item.thumbnail.pk

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            affiliate = FullAffiliate()
            affiliate.custom_thumbnail = None

            create_affiliate.return_value = affiliate
            update_affiliate_item_details(affiliate_item)

            assert not affiliate_item.thumbnail
            assert not ProductImage.objects.filter(pk=thumbnail_pk).count()

    def test_network_data_stock_records(self, affiliate_item, standard_size_factory):
        """It creates stock records for all sizes that match a standard size's number."""
        size_8 = standard_size_factory(8)
        size_10 = standard_size_factory(10)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            affiliate = FullAffiliate()
            affiliate.availability = [
                {'size': 8, 'is_regular': True},
                {'size': 12, 'is_regular': True}
            ]

            create_affiliate.return_value = affiliate
            update_affiliate_item_details(affiliate_item)

        availability_by_pk = {}
        stock_records = affiliate_item.stock_records.all()
        for record in stock_records:
            availability_by_pk[record.size.pk] = record.is_available

        assert availability_by_pk[size_8.pk]
        assert not availability_by_pk[size_10.pk]
        assert len(stock_records) == 2

    def test_network_data_stock_records_range(self, affiliate_item, standard_size_factory):
        """It maps numeric sizes to the range of standard sizes."""
        size_small = standard_size_factory(4, 6)
        size_medium = standard_size_factory(8, 10)
        size_large = standard_size_factory(12, 14)
        size_plus = standard_size_factory(16, 22)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            affiliate = FullAffiliate()
            affiliate.availability = [
                {'size': 8, 'is_regular': True},
                {'size': 14, 'is_regular': True},
                {'size': 18, 'is_regular': True}
            ]

            create_affiliate.return_value = affiliate
            update_affiliate_item_details(affiliate_item)

        availability_by_pk = {}
        stock_records = affiliate_item.stock_records.all()
        for record in stock_records:
            availability_by_pk[record.size.pk] = record.is_available

        assert len(stock_records) == 4
        assert not availability_by_pk[size_small.pk]
        assert availability_by_pk[size_medium.pk]
        assert availability_by_pk[size_large.pk]
        assert availability_by_pk[size_plus.pk]

    def test_network_data_stock_records_variants(self, affiliate_item, standard_size_factory):
        """It ignores reported availability for sizes outside of the item's garment's size types."""
        garment = affiliate_item.garment

        standard_size_factory(2)
        standard_size_factory(4)
        standard_size_factory(6, is_petite=True)
        standard_size_factory(8, is_petite=True)
        standard_size_factory(10, is_tall=True)
        standard_size_factory(12, is_tall=True)
        standard_size_factory(14, is_plus_sized=True)
        standard_size_factory(16, is_plus_sized=True)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            affiliate = FullAffiliate()
            affiliate.availability = [
                {'size': 2, 'is_regular': True},
                {'size': 6, 'is_petite': True},
                {'size': 10, 'is_tall': True},
                {'size': 14, 'is_plus_sized': True}
            ]
            create_affiliate.return_value = affiliate

            sizes_by_type = {}
            for size_field in ('regular', 'petite', 'tall', 'plus'):
                setattr(garment, 'is_%s_sized' % size_field, True)
                garment.save()

                update_affiliate_item_details(affiliate_item)
                sizes_by_type[size_field] = sorted([
                    record.size.canonical.range_lower
                    for record in affiliate_item.stock_records.all()
                    if record.is_available
                ])

        assert sizes_by_type['regular'] == [2]
        assert sizes_by_type['petite'] == [2, 6]
        assert sizes_by_type['tall'] == [2, 6, 10]
        assert sizes_by_type['plus'] == [2, 6, 10, 14]

    def test_network_data_stock_records_unlisted(self, affiliate_item, standard_size_factory):
        """It marks an item as available in all of its garment's size types if the returned availability records are all outside of those size types."""
        garment = affiliate_item.garment
        garment.is_regular_sized = False
        garment.is_petite_sized = True
        garment.save()

        standard_size_factory(2)
        standard_size_factory(4, is_petite=True)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            affiliate = FullAffiliate()
            affiliate.availability = [
                {'size': 2, 'is_regular': True}
            ]

            create_affiliate.return_value = affiliate
            update_affiliate_item_details(affiliate_item)

        records = affiliate_item.stock_records.all()
        assert len(records) == 2

        available = [r for r in records if r.is_available]
        assert len(available) == 1

        size = available[0].size
        assert size.canonical.range_lower == 4
        assert size.is_petite
        assert not size.is_regular

    def test_network_data_stock_records_in_stock(self, affiliate_item, standard_size_factory):
        """It creates in-stock records for all known sizes if an affiliate signals that an item is globally available."""
        standard_size_factory(8)
        standard_size_factory(10)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = InStockAffiliate()
            update_affiliate_item_details(affiliate_item)

        records = affiliate_item.stock_records.all()
        assert len(records) == 2
        assert all([r.is_available for r in records])

    def test_network_data_stock_records_in_stock_variants(self, affiliate_item, standard_size_factory):
        """It only creates in-stock records for sizes that match the item's garment's size types when global availability is specified."""
        garment = affiliate_item.garment

        standard_size_factory(6)
        standard_size_factory(8, is_petite=True)
        standard_size_factory(10, is_tall=True)
        standard_size_factory(12, is_plus_sized=True)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            affiliate = FullAffiliate()
            affiliate.availability = True
            create_affiliate.return_value = affiliate

            sizes_by_type = {}
            for size_field in ('regular', 'petite', 'tall', 'plus'):
                setattr(garment, 'is_%s_sized' % size_field, True)
                garment.save()

                update_affiliate_item_details(affiliate_item)
                sizes_by_type[size_field] = sorted([
                    record.size.canonical.range_lower
                    for record in affiliate_item.stock_records.all()
                    if record.is_available
                ])

        assert sizes_by_type['regular'] == [6]
        assert sizes_by_type['petite'] == [6, 8]
        assert sizes_by_type['tall'] == [6, 8, 10]
        assert sizes_by_type['plus'] == [6, 8, 10, 12]

    def test_network_data_stock_records_out_of_stock(self, affiliate_item, standard_size_factory):
        """It creates unavailable in-stock records for all known sizes if an affiliate signals that an item is globally unavailable."""
        standard_size_factory(8)
        standard_size_factory(10)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = OutOfStockAffiliate()
            update_affiliate_item_details(affiliate_item)

        records = affiliate_item.stock_records.all()
        assert len(records) == 2
        assert not any([r.is_available for r in records])

    def test_network_data_stock_records_out_of_stock_variants(self, affiliate_item, standard_size_factory):
        """It creates out-of-stock records for all sizes, even those outside a garment's size types, when global unavailability is specified."""
        standard_size_factory(6)
        standard_size_factory(8, is_petite=True)
        standard_size_factory(10, is_tall=True)
        standard_size_factory(12, is_plus_sized=True)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = OutOfStockAffiliate()
            update_affiliate_item_details(affiliate_item)

        records = affiliate_item.stock_records.all()
        assert len(records) == 4
        assert not any([r.is_available for r in records])

    def test_network_data_stock_records_existing(self, affiliate_item, standard_size_factory):
        """It updates stock records for items with existing records."""
        standard_size_factory(8)

        with mock.patch(CREATE_AFFILIATE) as create_affiliate:
            create_affiliate.return_value = InStockAffiliate()

            update_affiliate_item_details(affiliate_item)
            records = affiliate_item.stock_records.all()

            assert len(records) == 1
            stock_record_8 = records[0]
            created_pk = stock_record_8.pk

            stock_record_8.is_available = False
            stock_record_8.save()

            update_affiliate_item_details(affiliate_item)
            records = affiliate_item.stock_records.all()

            assert len(records) == 1
            stock_record_8 = records[0]
            updated_pk = stock_record_8.pk

        assert created_pk is not None
        assert created_pk == updated_pk

        assert stock_record_8.is_available
