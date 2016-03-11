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
                return {
                    'guid': url,
                    'name': 'Test'
                }

        child = Child()
        overview = child.request_overview('test-url')

        assert overview['guid'] == 'test-url'
        assert overview['name'] == 'Test'

    def test_request_overview_validate_guid(self):
        """It ensures that a child affiliate's overview has a valid GUID."""
        class Child(Affiliate):
            def provide_overview(self, url):
                return {
                    'guid': '',
                    'name': 'Name'
                }

        with pytest.raises(LookupError):
            Child().request_overview('url')

    def test_request_overview_validate_name(self):
        """It ensures that a child affiliate's overview has a valid name."""
        class Child(Affiliate):
            def provide_overview(self, url):
                return {
                    'guid': '1234',
                    'name': ''
                }

        with pytest.raises(LookupError):
            Child().request_overview('url')

    def test_request_overview_validate_extra(self):
        """It ensures that a child affiliate's overview does not contain additional data."""
        class Child(Affiliate):
            def provide_overview(self, url):
                return {
                    'oxblood': 'oxblood',
                    'guid': 'guid',
                    'name': 'name'
                }

        with pytest.raises(LookupError) as e:
            Child().request_overview('url')

        assert 'oxblood' in str(e)
