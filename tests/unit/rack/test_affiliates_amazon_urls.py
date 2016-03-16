from chiton.rack.affiliates.amazon.urls import extract_asin_from_url


class TestExtractASINFromURL:

    def test_canonical(self):
        """It extracts the ASIN from a canonical URL."""
        url = 'http://www.amazon.com/Tahari-ASL-Baron-Sleeve-A-Line/dp/B00ZGRB7S6'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_search_result(self):
        """It extracts the ASIN from a search-results URL."""
        url = 'http://www.amazon.com/Tahari-ASL-Baron-Short-Sleeve/dp/B00ZGRB7UY/ref=sr_1_1?s=apparel&ie=UTF8&qid=1457487821&sr=1-1&nodeID=7141123011&keywords=tahari+asl+baron+a+line'
        assert extract_asin_from_url(url) == 'B00ZGRB7UY'

    def test_bare(self):
        """It extracts the ASIN from a bare URL."""
        url = 'http://www.amazon.com/dp/B00ZGRB7S6'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_bare_tracking(self):
        """It extracts the ASIN from a bare URL with tracking."""
        url = 'http://www.amazon.com/dp/B00ZGRB7S6/ref=sr_1_13'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_product(self):
        """It extracts the ASIN from a product URL."""
        url = 'http://www.amazon.com/gp/product/B00ZGRB7S6'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_product_tracking(self):
        """It extracts the ASIN from a product URL with tracking."""
        url = 'http://www.amazon.com/gp/product/B00ZGRB7S6/ref=sr_1_13'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_product_view(self):
        """It extracts the ASIN from a product view URL."""
        url = 'http://www.amazon.com/gp/product/glance/B00ZGRB7S6'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_product_view_tracking(self):
        """It extracts the ASIN from a product view URL with tracking."""
        url = 'http://www.amazon.com/gp/product/glance/B00ZGRB7S6/ref=sr_1_13'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_short_url(self):
        """It extracts the ASIN from a bare URL without the www subdomain."""
        url = 'http://amazon.com/dp/B00ZGRB7S6'
        assert extract_asin_from_url(url) == 'B00ZGRB7S6'

    def test_similar(self):
        """It ignores an ASIN not found on amazon.com."""
        url = 'http://www.amazon.co.uk/dp/B00ZGRB7S6'
        assert extract_asin_from_url(url) is None
