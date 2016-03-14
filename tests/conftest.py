import pytest
from pytest_factoryboy import register as register_factory

from .helpers.factories.runway import BasicFactory, CategoryFactory
from .helpers.vcr import amazon_api_request, shopstyle_api_request

pytest.fixture()(amazon_api_request)
pytest.fixture()(shopstyle_api_request)

register_factory(BasicFactory)
register_factory(CategoryFactory)
