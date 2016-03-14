import pytest

from .helpers.vcr import amazon_api_request, shopstyle_api_request

pytest.fixture()(amazon_api_request)
pytest.fixture()(shopstyle_api_request)
