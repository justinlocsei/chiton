from decimal import Decimal

import pytest

from chiton.rack.affiliates.shopstyle import Affiliate
from chiton.rack.affiliates.exceptions import LookupError


class TestShopstyleAffiliate:

    def test_request_overview_valid_product_id(self, shopstyle_api_request):
        """It returns a name and GUID when using a URL with a valid product ID."""
        with shopstyle_api_request():
            overview = Affiliate().request_overview('http://api.shopstyle.com/action/apiVisitRetailer?id=471281504')

        assert overview['guid'] == '471281504'
        assert overview['name'] == 'J.Crew Double-breasted blazer'

    def test_request_overview_invalid_product_id(self, shopstyle_api_request):
        """It raises an error when an invalid product ID is used."""
        with shopstyle_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_overview('http://api.shopstyle.com/action/apiVisitRetailer?id=000000000')

    def test_request_overview_invalid_url(self):
        """It raises an error when an invalid URL is used."""
        with pytest.raises(LookupError):
            Affiliate().request_overview('http://www.shopstyle.com')

    def test_request_details_name(self, shopstyle_api_request):
        """It returns the item's name in its details."""
        with shopstyle_api_request():
            details = Affiliate().request_details('471281504')

        assert details['name'] == 'J.Crew Double-breasted blazer'

    def test_request_details_retailer(self, shopstyle_api_request):
        """It returns the item's retailer in its details."""
        with shopstyle_api_request():
            details = Affiliate().request_details('471281504')

        assert details['retailer'] == 'J.Crew'

    def test_request_details_price(self, shopstyle_api_request):
        """It returns the item's listed price in its details."""
        with shopstyle_api_request():
            details = Affiliate().request_details('471281504')

        assert details['price'] == Decimal('198.00')

    def test_request_details_price_sale(self, shopstyle_api_request):
        """It returns the item's sale price when one is provided."""
        with shopstyle_api_request():
            details = Affiliate().request_details('497747666')

        assert details['price'] == Decimal('49.99')

    def test_request_details_image(self, shopstyle_api_request):
        """It returns a primary and thumbnail image for the item."""
        with shopstyle_api_request():
            details = Affiliate().request_details('471281504')

        assert '.jpg' in details['images'][0]['url']
        assert '.jpg' in details['images'][1]['url']

        by_size = sorted(details['images'], key=lambda i: i['height'])

        assert by_size[0]['width'] < by_size[1]['width']
        assert by_size[0]['height'] < by_size[1]['height']

    def test_request_details_image_color(self, shopstyle_api_request):
        """It returns color-specific images when possible."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            default = affiliate.request_details('470750142')
            red = affiliate.request_details('470750142', colors=['Red'])
            purple = affiliate.request_details('470750142', colors=['Purple'])
            missing = affiliate.request_details('470750142', colors=['Orange Green'])

        assert '.jpg' in default['images'][0]['url']
        assert '.jpg' in default['images'][1]['url']
        assert '.jpg' in red['images'][0]['url']
        assert '.jpg' in red['images'][0]['url']
        assert '.jpg' in purple['images'][0]['url']
        assert '.jpg' in purple['images'][0]['url']

        assert default['images'][0]['url'] != red['images'][0]['url'] and default['images'][0]['url'] != purple['images'][0]['url']
        assert default['images'][1]['url'] != red['images'][1]['url'] and default['images'][1]['url'] != purple['images'][1]['url']

        assert default['images'][0]['url'] == missing['images'][0]['url']
        assert default['images'][1]['url'] == missing['images'][1]['url']

    def test_request_details_image_color_missing(self, shopstyle_api_request):
        """It returns the default image if no color-specific image is present."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            details = affiliate.request_details('521400855')
            with_color = affiliate.request_details('521400855', colors=['Black'])

        assert '.jpg' in details['images'][0]['url']
        assert '.jpg' in details['images'][1]['url']
        assert '.jpg' in with_color['images'][0]['url']
        assert '.jpg' in with_color['images'][1]['url']

    def test_request_details_image_color_preference(self, shopstyle_api_request):
        """It returns the image of the first color when multiple colors are provided."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            red = affiliate.request_details('470750142', colors=['Red'])
            purple = affiliate.request_details('470750142', colors=['Purple'])
            purple_first = affiliate.request_details('470750142', colors=['Purple', 'Red'])
            red_first = affiliate.request_details('470750142', colors=['Red', 'Purple'])

        assert red['images'][0]['url'] != purple['images'][0]['url']
        assert red['images'][1]['url'] != purple['images'][1]['url']

        assert purple_first['images'][0]['url'] == purple['images'][0]['url']
        assert purple_first['images'][1]['url'] == purple['images'][1]['url']
        assert red_first['images'][0]['url'] == red['images'][0]['url']
        assert red_first['images'][1]['url'] == red['images'][1]['url']

    def test_request_details_availability(self, shopstyle_api_request):
        """It returns unique availability information based off of the canonical sizes."""
        with shopstyle_api_request():
            details = Affiliate().request_details('470750142')

        assert details['availability'] is not None

        size_numbers = [a['size'] for a in details['availability']]
        assert len(size_numbers) == 5
        assert len(set(size_numbers)) == 5

        regular_sizes = [a['is_regular'] for a in details['availability']]
        assert len([s for s in regular_sizes if s]) == 5

    def test_request_details_availability_size(self, shopstyle_api_request):
        """It returns the lower bound of a size's range."""
        with shopstyle_api_request():
            blazer = Affiliate().request_details('504335769')

        size_numbers = [r['size'] for r in blazer['availability']]

        assert 4 in size_numbers
        assert 6 not in size_numbers

    def test_request_details_availability_size_name_number(self, shopstyle_api_request):
        """It returns a size number when a canonical size's name is only a number."""
        with shopstyle_api_request():
            trouser_jeans = Affiliate().request_details('457098007')

        size_numbers = [r['size'] for r in trouser_jeans['availability']]

        assert sorted(size_numbers) == [22, 24]

    def test_request_details_availability_variants(self, shopstyle_api_request):
        """It maps Shopstyle's canonical sizes to known size variants."""
        with shopstyle_api_request():
            pants = Affiliate().request_details('487070535')
            plus_size_dress = Affiliate().request_details('470962583')

        sizes_by_variant = {
            'regular': 0,
            'petite': 0,
            'tall': 0
        }
        for record in pants['availability']:
            if record['is_regular']:
                type_key = 'regular'
            elif record['is_petite']:
                type_key = 'petite'
            elif record['is_tall']:
                type_key = 'tall'

            sizes_by_variant[type_key] += 1

        assert all(sizes_by_variant.values())
        assert sum(sizes_by_variant.values()) == len(pants['availability'])

        assert all([s['is_plus_sized'] for s in plus_size_dress['availability']])
        assert not any([s['is_regular'] for s in plus_size_dress['availability']])

    def test_request_details_availability_color(self, shopstyle_api_request):
        """It can return color-specific availability information."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            default = affiliate.request_details('470750142')
            purple = affiliate.request_details('470750142', colors=['Purple'])

        assert default['availability'] is not None
        assert purple['availability'] is not None

        assert len(default['availability']) > len(purple['availability'])

    def test_request_details_availability_no_colors(self, shopstyle_api_request):
        """It returns size-specific availability when an item lacks color information but has canonical sizes."""
        with shopstyle_api_request():
            dress_no_colors = Affiliate().request_details('470962583')

        availability = dress_no_colors['availability']
        assert not isinstance(availability, bool)
        assert len(availability) > 0

    def test_request_details_availability_no_stock_records(self, shopstyle_api_request):
        """It signals global availability when no stock information is present but the item is marked as in stock."""
        with shopstyle_api_request():
            details = Affiliate().request_details('493153459')

        assert details['availability'] is True

    def test_request_details_availability_partial_stock_records(self, shopstyle_api_request):
        """It signals global availability when an item's stock records lack a size and color and the item is marked as in stock."""
        with shopstyle_api_request():
            details = Affiliate().request_details('494093141')

        assert details['availability'] is True

    def test_request_details_invalid_product_id(self, shopstyle_api_request):
        """It raises an error when looking up details for an inavlid product ID."""
        with shopstyle_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_details('0000000000')

    def test_request_raw(self, shopstyle_api_request):
        """It returns the full API response."""
        with shopstyle_api_request():
            raw = Affiliate().request_raw('471281504')

        assert raw['id'] == 471281504

    def test_request_raw_invalid_product_id(self, shopstyle_api_request):
        """It raises an error when getting a raw response for an invalid product ID."""
        with shopstyle_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_raw('0000000000')
