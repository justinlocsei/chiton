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

    def test_request_details_url(self, amazon_api_request, settings):
        """It returns a URL that contains the tracking ID."""
        settings.AMAZON_ASSOCIATES_TRACKING_ID = 'coveryourbasics-test-20'

        with amazon_api_request():
            details = Affiliate().request_details('B00ZGRB7S6')

        assert details['url'].startswith('http://www.amazon.com')
        assert 'tag=coveryourbasics-test-20' in details['url']

    def test_request_details_retailer(self, amazon_api_request):
        """It uses a fixed retailer."""
        with amazon_api_request():
            details = Affiliate().request_details('B00ZGRB7S6')

        assert details['retailer'] == 'Amazon'

    def test_request_details_colors(self, amazon_api_request):
        """It returns a list of item colors."""
        with amazon_api_request():
            details = Affiliate().request_details('B01D8N0PU0')

        assert details['colors'] == ['Black', 'Blue', 'Rose', 'Yellow']

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

        valid_urls = [url for url in details['images'] if '.jpg' in url]
        assert len(set(valid_urls)) == 2

    def test_request_details_image_color(self, amazon_api_request):
        """It returns color-specific images when possible."""
        affiliate = Affiliate()

        with amazon_api_request():
            default = affiliate.request_details('B00YJJ4SNS')
            green = affiliate.request_details('B00YJJ4SNS', colors=['Green'])
            missing = affiliate.request_details('B00YJJ4SNS', colors=['Orange Green'])

        assert '.jpg' in default['images'][0]
        assert '.jpg' in default['images'][1]
        assert '.jpg' in green['images'][0]
        assert '.jpg' in green['images'][1]

        assert default['images'][0] != green['images'][0]
        assert default['images'][1] != green['images'][1]

        assert default['images'][0] == missing['images'][0]
        assert default['images'][1] == missing['images'][1]

    def test_request_details_image_color_preference(self, amazon_api_request):
        """It gets the image for the first color in the list."""
        affiliate = Affiliate()

        with amazon_api_request():
            black = affiliate.request_details('B00YJJ4SNS', colors=['Black'])
            green = affiliate.request_details('B00YJJ4SNS', colors=['Green'])
            black_first = affiliate.request_details('B00YJJ4SNS', colors=['Black', 'Green'])
            green_first = affiliate.request_details('B00YJJ4SNS', colors=['Green', 'Black'])

        assert black['images'][0] != green['images'][0]
        assert black['images'][1] != green['images'][1]

        assert green_first['images'][0] == green['images'][0]
        assert green_first['images'][1] == green['images'][1]
        assert black_first['images'][0] == black['images'][0]
        assert black_first['images'][1] == black['images'][1]

    def test_request_details_image_incomplete(self, amazon_api_request):
        """It handles item variations that lack full image sets for a requested color."""
        with amazon_api_request():
            details = Affiliate().request_details('B00NZJJM1Q', colors=['Black'])

        assert '.jpg' in details['images'][0]
        assert '.jpg' in details['images'][1]

    def test_request_details_image_missing(self, amazon_api_request):
        """It falls back to variant items when the main item does not provide image data."""
        with amazon_api_request():
            details = Affiliate().request_details('B0116QTP20', colors=['Black'])

        assert '.jpg' in details['images'][0]
        assert '.jpg' in details['images'][1]

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

    def test_request_details_no_variations(self, amazon_api_request):
        """It fetches details when there are no item variations."""
        with amazon_api_request():
            details = Affiliate().request_details('B01HMLBAAI')

        assert details['availability'] is True
        assert 'B01HMLBAAI' in details['url']
        assert details['name'] == "What Goes Around Comes Around Women's Chanel Jacket (Previously Owned)"
        assert details['price'] == Decimal('2750.00')
        assert details['colors'] == ['Black']
        assert details['retailer'] == 'Amazon'
        assert len([i for i in details['images'] if i.endswith('.jpg')]) == 2

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

    def test_request_images(self, amazon_api_request):
        """It returns a list of image URLs."""
        with amazon_api_request():
            images = Affiliate().request_images('B00GOT8YQI')
            assert len(images) > 1

            valid_images = [i for i in images if '.jpg' in i]
            assert len(valid_images) == len(images)

    def test_request_images_unique(self, amazon_api_request):
        """It returns a list of unique image URLs."""
        with amazon_api_request():
            images = Affiliate().request_images('B00GOT8YQI')

            assert len(images) == len(set(images))

    def test_request_images_invalid_product_id(self, amazon_api_request):
        """It raises an error when requesting images for an invalid product ID."""
        with amazon_api_request():
            with pytest.raises(LookupError):
                Affiliate().request_images('0000000000')

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

    def test_is_url_valid(self, settings):
        """It flags any URLs with an incorrect tag as invalid."""
        settings.AMAZON_ASSOCIATES_TRACKING_ID = 'development'
        affiliate = Affiliate()

        assert affiliate.is_url_valid('https://www.amazon.com?tag=development')
        assert not affiliate.is_url_valid('https://www.amazon.com?tag=production')

    def test_is_url_valid_missing_tag(self):
        """It flags an item without a tracking tag as invalid."""
        affiliate = Affiliate()

        assert not affiliate.is_url_valid('https://www.amazon.com')
        assert not affiliate.is_url_valid('https://www.amazon.com?camp=2025')

    def test_is_url_valid_blank(self):
        """It flags an item without an affiliate URL as valid."""
        affiliate = Affiliate()

        assert affiliate.is_url_valid(None)
        assert affiliate.is_url_valid('')
