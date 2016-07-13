from decimal import Decimal
from urllib.error import HTTPError

import mock
import pytest

from chiton.rack.affiliates.amazon import Affiliate
from chiton.rack.affiliates.exceptions import LookupError, ThrottlingError


class TestAmazonAffiliate:

    @pytest.fixture
    def http_error_factory(self):
        def factory(code):
            return HTTPError(code=code, hdrs=None, fp=None, msg=None, url=None)

        return factory

    def test_connect(self):
        """It exposes a connection to the Amazon API."""
        assert Affiliate().connect()

    def test_request_overview_valid_asin(self, amazon_api_request):
        """It returns a name and GUID when using a URL with a valid ASIN."""
        with amazon_api_request():
            overview = Affiliate().request_overview('http://www.amazon.com/dp/B00ZGRB7S6')

        assert overview['guid'] == 'B00ZGRB7S6'
        assert overview['name'] == 'Tahari by ASL Baron Short Sleeve A-Line Dress, Red'

    def test_request_overview_valid_asin_parent_asin(self, amazon_api_request):
        """It returns the parent ASIN when given the URL for a child item."""
        with amazon_api_request():
            overview = Affiliate().request_overview('http://www.amazon.com/dp/B00ZGRB7UO')

        assert overview['guid'] == 'B00ZGRB7S6'
        assert overview['name'] == 'Tahari by ASL Baron Short Sleeve A-Line Dress, Red (16)'

    def test_request_overview_invalid_asin(self, amazon_api_request):
        """It raises an error when an invalid ASIN is used."""
        with amazon_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_overview('http://www.amazon.com/dp/0000000000')

    def test_request_overview_invalid_url(self):
        """It raises an error when an invalid URL is used."""
        with pytest.raises(LookupError):
            Affiliate().request_overview('http://www.amazon.com')

    def test_request_overview_throttling(self, http_error_factory):
        """It raises a throttling error in response to an HTTP 503 code."""
        affiliate = Affiliate()
        affiliate.connect = mock.Mock(side_effect=http_error_factory(503))

        with pytest.raises(ThrottlingError):
            affiliate.request_overview('http://www.amazon.com/dp/B00ZGRB7S6')

    def test_request_overview_http_error(self, http_error_factory):
        """It re-raises non-throttled HTTP errors."""
        affiliate = Affiliate()
        affiliate.connect = mock.Mock(side_effect=http_error_factory(400))

        with pytest.raises(HTTPError) as http_error:
            affiliate.request_overview('http://www.amazon.com/dp/B00ZGRB7S6')

        assert http_error.value.code == 400

    def test_request_details_name(self, amazon_api_request):
        """It returns the item's name."""
        with amazon_api_request():
            details = Affiliate().request_details('B00ZGRB7S6')

        assert details['name'] == 'Tahari by ASL Baron Short Sleeve A-Line Dress, Red'

    def test_request_details_retailer(self, amazon_api_request):
        """It uses a fixed retailer."""
        with amazon_api_request():
            details = Affiliate().request_details('B00ZGRB7S6')

        assert details['retailer'] == 'Amazon'

    def test_request_details_price(self, amazon_api_request):
        """It returns the average price of all item offers."""
        affiliate = Affiliate()

        with amazon_api_request():
            raw = affiliate.request_raw('B00ZGRB7S6')
            details = affiliate.request_details('B00ZGRB7S6')

        assert details['price'] == Decimal('69.99')

        prices = raw['Item']['VariationSummary']
        low_price = int(prices['LowestPrice']['Amount'])
        high_price = int(prices['HighestPrice']['Amount'])
        avg_price = int(details['price'] * 100)

        assert low_price <= avg_price <= high_price

    def test_request_details_image(self, amazon_api_request):
        """It returns a thumbnail and large image for the item."""
        with amazon_api_request():
            details = Affiliate().request_details('B00YJJ4SNS')

        image_urls = [image['url'] for image in details['images']]
        valid_urls = [url for url in image_urls if '.jpg' in url]
        assert len(set(valid_urls)) == 2

        by_size = sorted(details['images'], key=lambda i: i['height'])

        assert by_size[0]['width'] < by_size[1]['width']
        assert by_size[0]['height'] < by_size[1]['height']

    def test_request_details_image_color(self, amazon_api_request):
        """It returns color-specific images when possible."""
        affiliate = Affiliate()

        with amazon_api_request():
            default = affiliate.request_details('B00YJJ4SNS')
            green = affiliate.request_details('B00YJJ4SNS', colors=['Green'])
            missing = affiliate.request_details('B00YJJ4SNS', colors=['Orange Green'])

        assert '.jpg' in default['images'][0]['url']
        assert '.jpg' in default['images'][1]['url']
        assert '.jpg' in green['images'][0]['url']
        assert '.jpg' in green['images'][1]['url']

        assert default['images'][0]['url'] != green['images'][0]['url']
        assert default['images'][1]['url'] != green['images'][1]['url']

        assert default['images'][0]['url'] == missing['images'][0]['url']
        assert default['images'][1]['url'] == missing['images'][1]['url']

    def test_request_details_image_color_preference(self, amazon_api_request):
        """It gets the image for the first color in the list."""
        affiliate = Affiliate()

        with amazon_api_request():
            black = affiliate.request_details('B00YJJ4SNS', colors=['Black'])
            green = affiliate.request_details('B00YJJ4SNS', colors=['Green'])
            black_first = affiliate.request_details('B00YJJ4SNS', colors=['Black', 'Green'])
            green_first = affiliate.request_details('B00YJJ4SNS', colors=['Green', 'Black'])

        assert black['images'][0]['url'] != green['images'][0]['url']
        assert black['images'][1]['url'] != green['images'][1]['url']

        assert green_first['images'][0]['url'] == green['images'][0]['url']
        assert green_first['images'][1]['url'] == green['images'][1]['url']
        assert black_first['images'][0]['url'] == black['images'][0]['url']
        assert black_first['images'][1]['url'] == black['images'][1]['url']

    def test_request_details_image_incomplete(self, amazon_api_request):
        """It handles item variations that lack full image sets for a requested color."""
        with amazon_api_request():
            details = Affiliate().request_details('B00NZJJM1Q', colors=['Black'])

        assert '.jpg' in details['images'][0]['url']
        assert '.jpg' in details['images'][1]['url']

    def test_request_details_image_missing(self, amazon_api_request):
        """It falls back to variant items when the main item does not provide image data."""
        with amazon_api_request():
            details = Affiliate().request_details('B0116QTP20', colors=['Black'])

        assert '.jpg' in details['images'][0]['url']
        assert '.jpg' in details['images'][1]['url']

    def test_request_details_availability(self, amazon_api_request):
        """It marks every item as globally available."""
        with amazon_api_request():
            details = Affiliate().request_details('B00ZGRB7S6')

        assert details['availability'] is True

    def test_request_details_valid_asin_child(self, amazon_api_request):
        """It raises an error when requesting details for a child item."""
        with amazon_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_details('B00ZGRB7UO')

    def test_request_details_invalid_asin(self, amazon_api_request):
        """It raises an error when looking up details for an invalid ASIN."""
        with amazon_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_details('0000000000')

    def test_request_details_throttling(self, http_error_factory):
        """It raises a throttling error in response to an HTTP 503 code."""
        affiliate = Affiliate()
        affiliate.connect = mock.Mock(side_effect=http_error_factory(503))

        with pytest.raises(ThrottlingError):
            affiliate.request_details('B00ZGRB7S6')

    def test_request_details_http_error(self, http_error_factory):
        """It re-raises non-throttling HTTP errors."""
        affiliate = Affiliate()
        affiliate.connect = mock.Mock(side_effect=http_error_factory(400))

        with pytest.raises(HTTPError) as http_error:
            affiliate.request_details('B00ZGRB7S6')

        assert http_error.value.code == 400

    def test_request_raw(self, amazon_api_request):
        """It returns the full API response."""
        with amazon_api_request():
            raw = Affiliate().request_raw('B00ZGRB7UO')

        assert raw['Item']['ASIN'] == 'B00ZGRB7UO'

    def test_request_raw_invalid_asin(self, amazon_api_request):
        """It raises an error when getting a raw response for an invalid ASIN."""
        with amazon_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_raw('0000000000')

    def test_request_raw_throttling(self, http_error_factory):
        """It raises a throttling error in response to an HTTP 503 code."""
        affiliate = Affiliate()
        affiliate.connect = mock.Mock(side_effect=http_error_factory(503))

        with pytest.raises(ThrottlingError):
            affiliate.request_raw('B00ZGRB7S6')

    def test_request_raw_http_error(self, http_error_factory):
        """It re-raises non-throttling HTTP errors."""
        affiliate = Affiliate()
        affiliate.connect = mock.Mock(side_effect=http_error_factory(400))

        with pytest.raises(HTTPError) as http_error:
            affiliate.request_raw('B00ZGRB7S6')

        assert http_error.value.code == 400
