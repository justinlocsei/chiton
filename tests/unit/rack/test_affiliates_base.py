from decimal import Decimal

import pytest

from chiton.rack.affiliates.base import Affiliate
from chiton.rack.affiliates.exceptions import ConfigurationError, LookupError
from chiton.rack.affiliates.responses import ItemDetails, ItemOverview


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
                return ItemOverview(guid=url, name='Test')

        overview = Child().request_overview('test-url')

        assert overview.guid == 'test-url'
        assert overview.name == 'Test'

    def test_request_overview_format(self):
        """It ensures that a child affiliate's overview is an overview instance."""
        class Child(Affiliate):
            def provide_overview(self, guid):
                return {'name': 'Name'}

        with pytest.raises(LookupError):
            Child().request_overview('guid')

    def test_request_overview_errors(self):
        """It re-raises overview configuration errors."""
        class Child(Affiliate):
            def provide_overview(self, guid):
                raise ConfigurationError('Invalid GUID')

        with pytest.raises(LookupError) as error:
            Child().request_overview('guid')

        assert 'Invalid GUID' in str(error.value)

    def test_request_details(self):
        """It returns a child affiliate's details."""
        class Child(Affiliate):
            def provide_details(self, guid):
                return ItemDetails(price=Decimal('12.99'))

        details = Child().request_details('guid')
        assert details.price == Decimal('12.99')

    def test_request_details_format(self):
        """It ensures that a child affiliate's details are a details instance."""
        class Child(Affiliate):
            def provide_details(self, guid):
                return {'price': Decimal('12.99')}

        with pytest.raises(LookupError):
            Child().request_details('guid')

    def test_request_details_errors(self):
        """It re-raises details configuration errors."""
        class Child(Affiliate):
            def provide_details(self, guid):
                raise ConfigurationError('Invalid GUID')

        with pytest.raises(LookupError) as error:
            Child().request_details('guid')

        assert 'Invalid GUID' in str(error.value)
