from decimal import Decimal

import mock
import pytest

from chiton.core.exceptions import FormatError
from chiton.rack.affiliates.base import Affiliate
from chiton.rack.affiliates.exceptions import LookupError


class DefaultAffiliate(Affiliate):
    pass


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

    def test_configure_args(self):
        """It forwards all argument's to a child affiliate's configure method."""
        class Child(Affiliate):
            def configure(self, one, two=None):
                self.one = one
                self.two = two

        child = Child(1, two=2)

        assert child.one == 1
        assert child.two == 2

    def test_request_overview(self):
        """It allows a child affiliate to provide overview information."""
        class Child(Affiliate):
            def provide_overview(self, url):
                return {'guid': url, 'name': 'Test'}

        overview = Child().request_overview('test-url')

        assert overview['guid'] == 'test-url'
        assert overview['name'] == 'Test'

    def test_request_overview_error(self):
        """It raises an error when the overview has an invalid format."""
        class Child(Affiliate):
            def provide_overview(self, guid):
                return {}

        with mock.patch('chiton.rack.affiliates.base.ItemOverview') as ItemOverview:
            ItemOverview.side_effect = FormatError

            with pytest.raises(LookupError):
                Child().request_overview('url')

    def test_request_overview_empty(self):
        """It raises an error when an affiliate does not provide overviews."""
        with pytest.raises(NotImplementedError):
            DefaultAffiliate().request_overview('url')

    def test_request_details(self):
        """It returns a child affiliate's details with or without a color."""
        class Child(Affiliate):
            def provide_details(self, guid, colors):
                color = colors[0] if colors else None
                return {
                    'availability': True,
                    'image': {
                        'height': 100,
                        'url': 'http://%s%s.com' % (guid, color),
                        'width': 100
                    },
                    'name': 'Item Name',
                    'price': Decimal('12.99'),
                    'thumbnail': {
                        'height': 50,
                        'url': 'http://%s%s.net' % (guid, color),
                        'width': 50
                    }
                }

        affiliate = Child()
        without_color = affiliate.request_details('guid')
        with_color = affiliate.request_details('guid', colors=['Black'])

        assert without_color['price'] == Decimal('12.99')
        assert with_color['price'] == Decimal('12.99')
        assert without_color['name'] == 'Item Name'
        assert with_color['name'] == 'Item Name'
        assert without_color['availability']
        assert with_color['availability']

        assert without_color['image']['height'] == 100
        assert without_color['image']['width'] == 100
        assert without_color['thumbnail']['height'] == 50
        assert without_color['thumbnail']['width'] == 50

        assert without_color['image']['url'] == 'http://guidNone.com'
        assert without_color['thumbnail']['url'] == 'http://guidNone.net'

        assert with_color['image']['url'] == 'http://guidBlack.com'
        assert with_color['thumbnail']['url'] == 'http://guidBlack.net'

    def test_request_details_error(self):
        """It raises an error when the details have an invalid format."""
        class Child(Affiliate):
            def provide_details(self, guid, colors):
                return {}

        with mock.patch('chiton.rack.affiliates.base.ItemDetails') as ItemDetails:
            ItemDetails.side_effect = FormatError

            with pytest.raises(LookupError):
                Child().request_details('guid')

    def test_request_details_empty(self):
        """It raises an error when an affiliate does not provide detailss."""
        with pytest.raises(NotImplementedError):
            DefaultAffiliate().request_details('guid')

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

    def test_request_raw_empty(self):
        """It raises an error when an affiliate does not provide raw responses."""
        with pytest.raises(NotImplementedError):
            DefaultAffiliate().request_raw('guid')
