from chiton.rack.affiliates.shopstyle.urls import extract_product_id_from_api_url


class TestExtractProductIDFromAPIURL:

    def test_api_url(self):
        """It extracts the product ID from a valid API URL."""
        url = 'http://api.shopstyle.com/action/apiVisitRetailer?id=471281504&pid=uid3600-33034440-48'
        assert extract_product_id_from_api_url(url) == '471281504'

    def test_api_url_no_id(self):
        """It returns None if no ID is found in the query string."""
        url = 'http://api.shopstyle.com/action/apiVisitRetailer?pid=uid3600-33034440-48'
        assert extract_product_id_from_api_url(url) is None

    def test_api_url_no_query(self):
        """It returns None if no query string is present."""
        url = 'http://api.shopstyle.com/action/apiVisitRetailer'
        assert extract_product_id_from_api_url(url) is None
