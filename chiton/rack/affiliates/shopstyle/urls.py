from urllib.parse import parse_qs, urlparse

API_URL = 'api.shopstyle.com/action/apiVisitRetailer'


def extract_product_id_from_api_url(url):
    """Extract a Shopstyle product ID from an API URL.

    Args:
        url (str): An item's API URL

    Returns:
        str: The item's product ID, or None
    """
    if API_URL not in url:
        return None

    query = urlparse(url).query
    parsed = parse_qs(query)

    if 'id' in parsed:
        return parsed['id'][0]
    else:
        return None
