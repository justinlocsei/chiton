from django.conf import settings
import json
import requests

from chiton.rack.affiliates.shopstyle.urls import extract_product_id_from_api_url
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate
from chiton.rack.affiliates.exceptions import LookupError

# The base endpoint for the Shopstyle API
API_URL = 'http://api.shopstyle.com/api/v2'


class Affiliate(BaseAffiliate):
    """An affiliate for Shopstyle."""

    def provide_overview(self, url):
        product_id = extract_product_id_from_api_url(url)
        if product_id is None:
            raise LookupError('No product ID could be extracted from the URL %s' % url)

        response = self._request_product(product_id)
        parsed = self._validate_response(response, product_id)

        return {
            'guid': str(parsed['id']),
            'name': parsed['brandedName']
        }

    def provide_details(self, product_id):
        response = self._request_product(product_id)
        return self._validate_response(response, product_id)

    def provide_details_for_display(self, product_id):
        details = self.provide_details(product_id)

        details.pop('alternateImages', None)
        details.pop('image', None)

        for color in details.get('colors', []):
            color.pop('image', None)

        return details

    def _request_product(self, product_id):
        """Make a request for information on a single product.

        Args:
            product_id (str): The ID of a product

        Returns:
            requests.Response: The API response
        """
        endpoint = '%s/products/%s' % (API_URL, product_id)
        return requests.get(endpoint, params={
            'format': 'json',
            'pid': settings.SHOPSTYLE_UID
        })

    def _validate_response(self, response, product_id):
        """Validate an API response.

        Args:
            response (requests.Response): An HTTP response
            product_id (str): The product ID associated with the response

        Returns:
            dict: The parsed, valid response
        """
        if response.status_code != 200:
            raise LookupError('Invalid lookup for product %s: %s' % (product_id, response.text))

        return json.loads(response.text)
