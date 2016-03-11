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
            with pytest.raises(LookupError) as e:
                affiliate.request_overview('http://www.amazon.com/dp/0000000000')

        assert '0000000000' in str(e.value)

    def test_request_overview_invalid_url(self):
        """It raises an error when an invalid URL is used."""
        affiliate = Affiliate()

        with pytest.raises(LookupError):
            affiliate.request_overview('http://www.amazon.com')
