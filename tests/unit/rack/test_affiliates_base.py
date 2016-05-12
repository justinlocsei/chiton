from decimal import Decimal

import pytest

from chiton.rack.affiliates.base import Affiliate
from chiton.rack.affiliates.exceptions import LookupError


class TestBaseAffiliate:

    def test_configure(self):
        """It allows a child affiliate to perform initial configuration."""
        class Child(Affiliate):
            def configure(self):
                self.is_child = True

        affiliate = Affiliate()
        child = Child()

        assert not hasattr(affiliate, 'is_child')
        assert child.is_child is True

    def test_request_overview(self):
        """It allows a child affiliate to provide overview information."""
        class Child(Affiliate):
            def provide_overview(self, url):
                return {'guid': url, 'name': 'Test'}

        overview = Child().request_overview('test-url')

        assert overview.guid == 'test-url'
        assert overview.name == 'Test'

    def test_request_overview_format(self):
        """It ensures that a child affiliate's overview has all required fields."""
        class Child(Affiliate):
            def provide_overview(self, guid):
                return {'name': 'Name'}

        with pytest.raises(LookupError):
            Child().request_overview('guid')

    def test_request_details(self):
        """It returns a child affiliate's details with or without a color."""
        class Child(Affiliate):
            def provide_details(self, guid, color):
                return {
                    'image': {
                        'height': 100,
                        'url': 'http://%s%s.com' % (guid, color),
                        'width': 100
                    },
                    'price': Decimal('12.99'),
                    'thumbnail': {
                        'height': 50,
                        'url': 'http://%s%s.net' % (guid, color),
                        'width': 50
                    }
                }

        affiliate = Child()
        without_color = affiliate.request_details('guid')
        with_color = affiliate.request_details('guid', 'Black')

        assert without_color.price == Decimal('12.99')
        assert without_color.image.height == 100
        assert without_color.image.width == 100
        assert without_color.thumbnail.height == 50
        assert without_color.thumbnail.width == 50

        assert without_color.image.url == 'http://guidNone.com'
        assert without_color.thumbnail.url == 'http://guidNone.net'

        assert with_color.image.url == 'http://guidBlack.com'
        assert with_color.thumbnail.url == 'http://guidBlack.net'

    def test_request_details_format(self):
        """It ensures that a child affiliate's details have all required fields."""
        class Child(Affiliate):
            def provide_details(self, guid, color):
                return {}

        with pytest.raises(LookupError):
            Child().request_details('guid')

    def test_request_raw(self):
        """It returns a child affiliate's raw API response."""
        class Child(Affiliate):
            def provide_raw(self, guid):
                return {'raw': guid}

        raw = Child().request_raw('guid')
        assert raw['raw'] == 'guid'

    def test_request_raw_format(self):
        """It ensures that a raw API response is a dict."""
        class Child(Affiliate):
            def provide_raw(self, guid):
                return guid

        with pytest.raises(LookupError):
            Child().request_raw('guid')
