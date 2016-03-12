import pytest

from chiton.rack.affiliates import create_affiliate_from_slug
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate


class TestCreateAffiliateFromSlug:

    def test_valid_module(self):
        """It creates a new affiliate when given a valid module name."""
        affiliate = create_affiliate_from_slug('base')
        assert isinstance(affiliate, BaseAffiliate)

    def test_invalid_module(self):
        """It raises an error when given an invalid module name."""
        with pytest.raises(ImportError):
            create_affiliate_from_slug('unknown')
