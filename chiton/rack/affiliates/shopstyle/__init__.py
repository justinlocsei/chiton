import json

from django.conf import settings
from moneyed import Money, USD
import requests

from chiton.rack.affiliates.shopstyle.urls import extract_product_id_from_api_url
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate
from chiton.rack.affiliates.exceptions import LookupError


class Affiliate(BaseAffiliate):
    """An affiliate for Shopstyle."""

    _API_URL = 'http://api.shopstyle.com/api/v2'

    def provide_overview(self, url):
        product_id = extract_product_id_from_api_url(url)
        if product_id is None:
            raise LookupError('No product ID could be extracted from the URL: %s' % url)

        response = self._request_product(product_id)
        parsed = self._validate_response(response, product_id)

        return {
            'guid': str(parsed['id']),
            'name': parsed['brandedName']
        }

    def provide_details(self, product_id, color):
        response = self._request_product(product_id)
        parsed = self._validate_response(response, product_id)

        price = Money(str(parsed['price']), USD)
        image = self._find_image(parsed, 'XLarge', color)
        thumbnail = self._find_image(parsed, 'Medium', color)

        return {
            'image': image,
            'price': price.amount,
            'thumbnail': thumbnail
        }

    def provide_raw(self, product_id):
        response = self._request_product(product_id)
        return self._validate_response(response, product_id)

    def _find_image(self, parsed, size_name, color_name):
        """Find an image of a given size for an item of a given color.

        If no explicit image of the item in the given color can be found, this
        will fall back to using the generic product image.

        Args:
            parsed (dict): A parsed API response
            size_name (str): The name of the image size to use
            color_name (str): The name of the color to search for

        Returns:
            dict: Information on the image in the details image format
        """
        image = None
        color_match = (color_name or '').lower()

        for color in parsed['colors']:
            for canonical_color in color['canonicalColors']:
                if canonical_color['name'].lower() == color_match and 'image' in color:
                    image = color['image']['sizes'][size_name]

        if image is None:
            image = parsed['image']['sizes'][size_name]

        return {
            'height': image['actualHeight'],
            'url': image['url'],
            'width': image['actualWidth']
        }

    def _request_product(self, product_id):
        """Make a request for information on a single product.

        Args:
            product_id (str): The ID of a product

        Returns:
            requests.Response: The API response
        """
        endpoint = '%s/products/%s' % (self._API_URL, product_id)
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
