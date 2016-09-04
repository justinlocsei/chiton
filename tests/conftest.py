import pytest
from pytest_factoryboy import register as register_factory

from .helpers.environment import isolate_cache_tests
from .helpers.factories.closet import BrandFactory, CanonicalSizeFactory, ColorFactory, GarmentFactory, standard_size_factory
from .helpers.factories.rack import AffiliateItemFactory, AffiliateNetworkFactory, item_image_factory, StockRecordFactory
from .helpers.factories.runway import BasicFactory, CategoryFactory, FormalityFactory, ProprietyFactory, StyleFactory
from .helpers.factories.wintour import pipeline_profile_factory, wardrobe_profile_factory, PersonFactory, RecommendationFactory
from .helpers.vcr import amazon_api_request, record_request, shopstyle_api_request

pytest.fixture()(amazon_api_request)
pytest.fixture()(item_image_factory)
pytest.fixture()(pipeline_profile_factory)
pytest.fixture()(record_request)
pytest.fixture()(shopstyle_api_request)
pytest.fixture()(standard_size_factory)
pytest.fixture()(wardrobe_profile_factory)

register_factory(AffiliateItemFactory)
register_factory(AffiliateNetworkFactory)
register_factory(BasicFactory)
register_factory(BrandFactory)
register_factory(CanonicalSizeFactory)
register_factory(CategoryFactory)
register_factory(ColorFactory)
register_factory(FormalityFactory)
register_factory(GarmentFactory)
register_factory(PersonFactory)
register_factory(ProprietyFactory)
register_factory(RecommendationFactory)
register_factory(StockRecordFactory)
register_factory(StyleFactory)

pytest.fixture(autouse=True)(isolate_cache_tests)
