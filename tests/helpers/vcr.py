from functools import partial
import os.path
import urllib.parse as urlparse

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


def match_amazon_api_request(r1, r2):
    """Ignore the timestamp and signature in Amazon API requests."""
    p1 = pin_amazon_api_request_url(r1.uri)
    p2 = pin_amazon_api_request_url(r2.uri)
    return p1 == p2


def pin_amazon_api_request_url(url):
    """Return an Amazon API request URL without transient information."""
    parsed = urlparse.urlparse(url)

    query = urlparse.parse_qs(parsed.query)
    query.pop('Signature')
    query.pop('Timestamp')

    rebuilt = list(parsed)
    rebuilt[4] = urlparse.urlencode(query)

    return urlparse.urlunparse(rebuilt)


@pytest.fixture
def amazon_api_request(request):
    vcr = VCR()
    vcr.register_matcher('amazon_api', match_amazon_api_request)
    vcr.match_on = ['amazon_api']

    cassette_path = request_to_cassette_path(request)

    return partial(vcr.use_cassette, cassette_path)
