import pytest
from pytest_factoryboy import register as register_factory

from .helpers.factories.closet import BrandFactory, CanonicalSizeFactory, GarmentFactory, standard_size_factory
from .helpers.factories.rack import AffiliateItemFactory, AffiliateNetworkFactory, ProductImageFactory
from .helpers.factories.runway import BasicFactory, CategoryFactory, FormalityFactory, StyleFactory
from .helpers.factories.wintour import pipeline_profile_factory, wardrobe_profile_factory
from .helpers.vcr import amazon_api_request, shopstyle_api_request

pytest.fixture()(amazon_api_request)
pytest.fixture()(pipeline_profile_factory)
pytest.fixture()(shopstyle_api_request)
pytest.fixture()(standard_size_factory)
pytest.fixture()(wardrobe_profile_factory)

register_factory(AffiliateItemFactory)
register_factory(AffiliateNetworkFactory)
register_factory(BasicFactory)
register_factory(BrandFactory)
register_factory(CanonicalSizeFactory)
register_factory(CategoryFactory)
register_factory(FormalityFactory)
register_factory(GarmentFactory)
register_factory(ProductImageFactory)
register_factory(StyleFactory)
