import pytest
from pytest_factoryboy import register as register_factory

from .helpers.factories.closet import BrandFactory, GarmentFactory
from .helpers.factories.rack import AffiliateNetworkFactory
from .helpers.factories.runway import BasicFactory, CategoryFactory
from .helpers.vcr import amazon_api_request, shopstyle_api_request

pytest.fixture()(amazon_api_request)
pytest.fixture()(shopstyle_api_request)

register_factory(AffiliateNetworkFactory)
register_factory(BasicFactory)
register_factory(BrandFactory)
register_factory(CategoryFactory)
register_factory(GarmentFactory)
