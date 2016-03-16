from urllib.parse import parse_qs, urlparse

API_HOST = 'api.shopstyle.com'
API_PATH = '/action/apiVisitRetailer'


def extract_product_id_from_api_url(url):
    """Extract a Shopstyle product ID from an API URL.

    Args:
        url (str): An item's API URL

    Returns:
        str: The item's product ID, or None
    """
    parsed = urlparse(url)
    if parsed.hostname != API_HOST or parsed.path != API_PATH:
        return None

    query = parse_qs(parsed.query)

    if 'id' in query:
        return query['id'][0]
    else:
        return None
