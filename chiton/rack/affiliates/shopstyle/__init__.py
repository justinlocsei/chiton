import json
import re

from django.conf import settings
from moneyed import Money, USD
import requests

from chiton.rack.affiliates.shopstyle.urls import extract_product_id_from_api_url
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate
from chiton.rack.affiliates.exceptions import LookupError


# Matches for extracting numeric sizes from canonical-size names
SIZE_NUMBER_MATCH = re.compile(r'(\d+)')
SIZE_RANGE_MATCH = re.compile(r'\s+\((\d+(-\d+)?)\)$')

# The names used for size variants
SIZE_TALL = 'Tall'
SIZE_PETITE = 'Petite'
SIZE_PLUS = 'Plus'

# Desired image sizes
IMAGE_SIZES = ('Medium', 'XLarge')


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

    def provide_details(self, product_id, color_names):
        response = self._request_product(product_id)
        parsed = self._validate_response(response, product_id)

        price = Money(str(parsed.get('salePrice', parsed['price'])), USD)

        image_searches = [self._find_image(parsed, size, color_names) for size in IMAGE_SIZES]
        images = [image for image in image_searches if image]

        found_sizes = self._check_stock(parsed, color_names)
        if found_sizes:
            availability = [self._parse_size(size) for size in found_sizes]
        else:
            availability = parsed.get('inStock', False)

        return {
            'availability': availability,
            'images': images,
            'name': parsed['brandedName'],
            'price': price.amount
        }

    def provide_raw(self, product_id):
        response = self._request_product(product_id)
        return self._validate_response(response, product_id)

    def _find_image(self, parsed, size_name, color_names):
        """Find an image of a given size for an item of a given color.

        If no explicit image of the item in the given color can be found, this
        will fall back to using the generic product image.

        Args:
            parsed (dict): A parsed API response
            size_name (str): The name of the image size to use
            color_names (list): The names of the colors to search for

        Returns:
            dict: Information on the image in the details image format
        """
        image = None
        color_images = {}
        color_matches = [cn.lower() for cn in color_names]

        if color_matches:
            for color in parsed['colors']:
                if 'image' not in color:
                    continue
                for canonical_color in color['canonicalColors']:
                    canonical_name = canonical_color['name'].lower()
                    if canonical_name in color_matches:
                        color_images[canonical_name] = color['image']['sizes'][size_name]

        for color_match in color_matches:
            image = color_images.get(color_match, None)
            if image:
                break

        if image is None:
            image = parsed['image']['sizes'][size_name]

        return {
            'height': image['actualHeight'],
            'url': image['url'],
            'width': image['actualWidth']
        }

    def _check_stock(self, parsed, color_names):
        """Return the unique names of all available sizes.

        This checks Shopstyle's stock records, and adds any size whose name maps
        to a canonical size and whose color name maps to a canonical color whose
        name equals the given color name.  If no color name is provided, only
        size information will be used to determine availability.

        Args:
            parsed (dict): A parsed API response
            color_names (list): The names of the colors to check for

        Returns:
            set: Information on all available sizes
        """
        item_colors = parsed.get('colors', [])
        has_colors = len(item_colors) > 0

        stock_colors = []
        if color_names:
            color_searches = [cn.lower() for cn in color_names]
            for color in item_colors:
                canonical = color.get('canonicalColors', [])
                has_match = any([c for c in canonical if c['name'].lower() in color_searches])
                if has_match:
                    stock_colors.append(color['name'])

        stock_sizes = {}
        for size in parsed.get('sizes', []):
            canonical = size.get('canonicalSize', None)
            if canonical:
                stock_sizes[size['name']] = canonical

        found_sizes = set()
        sizes = []
        for stock in parsed.get('stock', []):
            if 'size' in stock and ('color' in stock or not has_colors):
                color_match = not stock_colors or stock['color']['name'] in stock_colors
                canonical = stock_sizes.get(stock['size']['name'], None)
                if color_match and canonical and canonical['name'] not in found_sizes:
                    sizes.append(canonical)
                    found_sizes.add(canonical['name'])

        return sizes

    def _parse_size(self, size):
        """Parse a Shopstyle size into a response-friendly format.

        Args:
            size (dict): Size information as returned by the Shopstyle API

        Returns:
            dict: Size information packaged for an availability response
        """
        name = size['name']

        size_range = SIZE_RANGE_MATCH.search(name)
        if size_range:
            raw_size = size_range.groups()[0].split('-')[0]
        else:
            raw_size = SIZE_NUMBER_MATCH.search(name).groups()[0]
        size_number = int(raw_size)

        variant_name = size.get('variant', None)
        is_petite = variant_name == SIZE_PETITE
        is_plus_sized = variant_name == SIZE_PLUS
        is_tall = variant_name == SIZE_TALL

        return {
            'is_petite': is_petite,
            'is_plus_sized': is_plus_sized,
            'is_regular': not any([is_petite, is_plus_sized, is_tall]),
            'is_tall': is_tall,
            'size': size_number
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
