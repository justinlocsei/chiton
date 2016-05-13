from decimal import Decimal

import pytest

from chiton.rack.affiliates.amazon import Affiliate
from chiton.rack.affiliates.exceptions import LookupError


class TestAmazonAffiliate:

    def test_request_overview_valid_asin(self, amazon_api_request):
        """It returns a name and GUID when using a URL with a valid ASIN."""
        affiliate = Affiliate()

        with amazon_api_request():
            overview = affiliate.request_overview('http://www.amazon.com/dp/B00ZGRB7S6')

        assert overview.guid == 'B00ZGRB7S6'
        assert overview.name == 'Tahari by ASL Baron Short Sleeve A-Line Dress, Red'

    def test_request_overview_valid_asin_parent_asin(self, amazon_api_request):
        """It returns the parent ASIN when given the URL for a child item."""
        affiliate = Affiliate()

        with amazon_api_request():
            overview = affiliate.request_overview('http://www.amazon.com/dp/B00ZGRB7UO')

        assert overview.guid == 'B00ZGRB7S6'
        assert overview.name == 'Tahari by ASL Baron Short Sleeve A-Line Dress, Red (16)'

    def test_request_overview_invalid_asin(self, amazon_api_request):
        """It raises an error when an invalid ASIN is used."""
        affiliate = Affiliate()

        with amazon_api_request():
            with pytest.raises(LookupError):
                affiliate.request_overview('http://www.amazon.com/dp/0000000000')

    def test_request_overview_invalid_url(self):
        """It raises an error when an invalid URL is used."""
        affiliate = Affiliate()

        with pytest.raises(LookupError):
            affiliate.request_overview('http://www.amazon.com')

    def test_request_details_price(self, amazon_api_request):
        """It returns the average price of all item offers."""
        affiliate = Affiliate()

        with amazon_api_request():
            raw = affiliate.request_raw('B00ZGRB7S6')
            details = affiliate.request_details('B00ZGRB7S6')

        assert details.price == Decimal('69.99')

        prices = raw['Item']['VariationSummary']
        low_price = int(prices['LowestPrice']['Amount'])
        high_price = int(prices['HighestPrice']['Amount'])
        avg_price = int(details.price * 100)

        assert low_price <= avg_price <= high_price

    def test_request_details_image(self, amazon_api_request):
        """It returns information on the item's images."""
        affiliate = Affiliate()

        with amazon_api_request():
            details = affiliate.request_details('B00YJJ4SNS')

        assert '.jpg' in details.image.url
        assert '.jpg' in details.thumbnail.url

        assert details.image.width > details.thumbnail.width
        assert details.image.height > details.thumbnail.height

    def test_request_details_image_color(self, amazon_api_request):
        """It returns color-specific images when possible."""
        affiliate = Affiliate()

        with amazon_api_request():
            default = affiliate.request_details('B00YJJ4SNS')
            green = affiliate.request_details('B00YJJ4SNS', colors=['Green'])
            missing = affiliate.request_details('B00YJJ4SNS', colors=['Orange Green'])

        assert '.jpg' in default.image.url
        assert '.jpg' in default.thumbnail.url
        assert '.jpg' in green.image.url
        assert '.jpg' in green.image.url

        assert default.image.url != green.image.url
        assert default.thumbnail.url != green.thumbnail.url

        assert default.image.url == missing.image.url
        assert default.thumbnail.url == missing.thumbnail.url

    def test_request_details_image_color_preference(self, amazon_api_request):
        """It gets the image for the first color in the list."""
        affiliate = Affiliate()

        with amazon_api_request():
            black = affiliate.request_details('B00YJJ4SNS', colors=['Black'])
            green = affiliate.request_details('B00YJJ4SNS', colors=['Green'])
            black_first = affiliate.request_details('B00YJJ4SNS', colors=['Black', 'Green'])
            green_first = affiliate.request_details('B00YJJ4SNS', colors=['Green', 'Black'])

        assert black.image.url != green.image.url
        assert black.thumbnail.url != green.thumbnail.url

        assert green_first.image.url == green.image.url
        assert green_first.thumbnail.url == green.thumbnail.url
        assert black_first.image.url == black.image.url
        assert black_first.thumbnail.url == black.thumbnail.url

    def test_request_details_availability(self, amazon_api_request):
        """It does not return item availability records."""
        affiliate = Affiliate()

        with amazon_api_request():
            details = affiliate.request_details('B00ZGRB7S6')

        assert details.availability is None

    def test_request_details_valid_asin_child(self, amazon_api_request):
        """It raises an error when requesting details for a child item."""
        affiliate = Affiliate()

        with amazon_api_request():
            with pytest.raises(LookupError):
                affiliate.request_details('B00ZGRB7UO')

    def test_request_details_invalid_asin(self, amazon_api_request):
        """It raises an error when looking up details for an inavlid ASIN."""
        affiliate = Affiliate()

        with amazon_api_request():
            with pytest.raises(LookupError):
                affiliate.request_details('0000000000')

    def test_request_raw(self, amazon_api_request):
        """It returns the full API response."""
        affiliate = Affiliate()

        with amazon_api_request():
            raw = affiliate.request_raw('B00ZGRB7UO')

        assert raw['Item']['ASIN'] == 'B00ZGRB7UO'

    def test_request_raw_invalid_asin(self, amazon_api_request):
        """It raises an error when getting a raw response for an inavlid ASIN."""
        affiliate = Affiliate()

        with amazon_api_request():
            with pytest.raises(LookupError):
                affiliate.request_raw('0000000000')
