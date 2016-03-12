import pytest

from chiton.rack.affiliates.shopstyle import Affiliate
from chiton.rack.affiliates.exceptions import LookupError


class TestShopstyleAffiliate:

    def test_request_overview_valid_product_id(self, shopstyle_api_request):
        """It returns a name and GUID when using a URL with a valid product ID."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            overview = affiliate.request_overview('http://api.shopstyle.com/action/apiVisitRetailer?id=471281504')
            assert overview['guid'] == '471281504'
            assert overview['name'] == 'J.Crew Double-breasted blazer'

    def test_request_overview_invalid_product_id(self, shopstyle_api_request):
        """It raises an error when an invalid product ID is used."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            with pytest.raises(LookupError):
                affiliate.request_overview('http://api.shopstyle.com/action/apiVisitRetailer?id=000000000')

    def test_request_overview_invalid_url(self):
        """It raises an error when an invalid URL is used."""
        affiliate = Affiliate()

        with pytest.raises(LookupError):
            affiliate.request_overview('http://www.shopstyle.com')

    def test_request_details_valid_product_id(self, shopstyle_api_request):
        """It returns item details when given a valid product ID."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            details = affiliate.request_details('471281504')
            assert details['brand']['name'] == 'J.Crew'
            assert details['categories'][0]['name'] == 'Blazers'

    def test_request_details_invalid_product_id(self, shopstyle_api_request):
        """It raises an error when looking up details for an inavlid product ID."""
        affiliate = Affiliate()

        with shopstyle_api_request():
            with pytest.raises(LookupError):
                affiliate.request_details('0000000000')
