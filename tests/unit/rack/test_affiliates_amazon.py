import pytest

from chiton.rack.affiliates.amazon import Affiliate
from chiton.rack.affiliates.exceptions import LookupError


class TestAmazonAffiliate:

    def test_request_overview_valid_asin(self, amazon_api_request):
        """It returns a name and GUID when using a URL with a valid ASIN."""
        affiliate = Affiliate()

        with amazon_api_request():
            overview = affiliate.request_overview('http://www.amazon.com/dp/B00ZGRB7UO')

        assert overview['guid'] == 'B00ZGRB7UO'
        assert overview['name'] == 'Tahari by ASL Baron Short Sleeve A-Line Dress, Red (16)'

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

    def test_request_details_valid_asin(self, amazon_api_request):
        """It returns item details when given a valid ASIN."""
        affiliate = Affiliate()

        with amazon_api_request():
            details = affiliate.request_details('B00ZGRB7UO')

        assert details['Department'] == 'womens'
        assert details['Brand'] == 'Tahari'

    def test_request_details_invalid_asin(self, amazon_api_request):
        """It raises an error when looking up details for an inavlid ASIN."""
        affiliate = Affiliate()

        with amazon_api_request():
            with pytest.raises(LookupError):
                affiliate.request_details('0000000000')
