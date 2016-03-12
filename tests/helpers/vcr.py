from functools import partial
import os.path

from inflection import underscore
import pytest
from vcr import VCR


def request_to_cassette_path(request):
    """Generate a path to a VCR cassette from a py.test request."""
    paths = ['tests', 'fixtures', 'vcr']
    paths += request.module.__name__.split('.')

    if request.cls:
        paths.append(underscore(request.cls.__name__))
    paths.append('%s.yml' % request.function.__name__)

    return os.path.join(*paths)


@pytest.fixture
def amazon_api_request(request):
    vcr = VCR()

    return partial(vcr.use_cassette,
        request_to_cassette_path(request),
        filter_query_parameters=['AssociateTag', 'AWSAccessKeyId', 'Signature', 'Timestamp'])


@pytest.fixture
def shopstyle_api_request(request):
    vcr = VCR()

    return partial(vcr.use_cassette,
        request_to_cassette_path(request),
        filter_query_parameters=['pid'])
