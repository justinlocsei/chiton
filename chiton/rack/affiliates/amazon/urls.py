import re
from urllib.parse import urlparse


FORMATS = [
    re.compile('/dp/(?P<asin>[A-Z0-9]{10})(/|$)?'),
    re.compile('/gp/product/([^/]+/)?(?P<asin>[A-Z0-9]{10})(/|$)?'),
]


def extract_asin_from_url(url):
    """Extract an Amazon ASIN from a product URL.

    Args:
        url (str): An item's URL

    Returns:
        str: The item's ASIN, or None
    """
    path = urlparse(url).path

    for format in FORMATS:
        match = format.search(path)
        if match and match.group('asin'):
            return match.group('asin')

    return None
