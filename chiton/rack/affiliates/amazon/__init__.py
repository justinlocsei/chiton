from collections import OrderedDict
from contextlib import contextmanager
import urllib
from urllib.error import HTTPError

import bottlenose
from decimal import Decimal
from django.conf import settings
import xmltodict

from chiton.core.uris import extract_query_param
from chiton.rack.affiliates.amazon.urls import extract_asin_from_url
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate
from chiton.rack.affiliates.exceptions import LookupError, ThrottlingError


# The desired image sizes to use from a response
IMAGE_SIZES = ('MediumImage', 'LargeImage')


@contextmanager
def raise_throttling_exception():
    """Re-raise throttling HTTP errors as throttling errors.

    Raises:
        chiton.rack.affiliates.exceptions.ThrottlingError: When an API call is throttled
    """
    try:
        yield
    except HTTPError as e:
        if e.code == 503:
            raise ThrottlingError()
        else:
            raise e


class Affiliate(BaseAffiliate):
    """An affiliate for Amazon Associates."""

    def provide_overview(self, url):
        asin = extract_asin_from_url(url)
        if asin is None:
            raise LookupError('No ASIN could be extracted from the URL: %s' % url)

        with raise_throttling_exception():
            response = self.connect().ItemLookup(ItemId=asin, ResponseGroup='Small')

        validated = self._validate_response(response, asin)
        item = validated['Items']['Item']
        name = item.get('ItemAttributes', {}).get('Title', None)

        asin = item['ASIN']
        parent_asin = item.get('ParentASIN', None)
        if parent_asin != asin:
            asin = parent_asin

        return {
            'guid': asin,
            'name': name
        }

    def provide_details(self, asin, colors):
        item = self._request_combined_data(asin)['Items']['Item']

        if 'Variations' not in item:
            raise LookupError('Details may not be provided for a child ASIN')

        variations = self._extract_variations(item)
        price = self._calculate_price(variations)
        images = [self._find_color_image(variations, size, colors) for size in IMAGE_SIZES]

        return {
            'availability': True,
            'colors': self._find_colors(variations),
            'images': images,
            'name': item['ItemAttributes']['Title'],
            'price': price,
            'retailer': 'Amazon',
            'url': urllib.parse.unquote(item['DetailPageURL'])
        }

    def provide_images(self, asin):
        data = self._request_combined_data(asin)['Items']['Item']
        return sorted(set(self._find_images(data, IMAGE_SIZES)))

    def provide_raw(self, asin):
        data = self._request_combined_data(asin)
        return data['Items']

    def provide_url_validity(self, url):
        if not url:
            return True
        else:
            return extract_query_param(url, 'tag') == [settings.AMAZON_ASSOCIATES_TRACKING_ID]

    def connect(self):
        """Return a connection to the Amazon Associates API.

        Returns:
            bottlenose.Amazon: A connection to the API
        """
        return bottlenose.Amazon(
            settings.AMAZON_ASSOCIATES_AWS_ACCESS_KEY_ID,
            settings.AMAZON_ASSOCIATES_AWS_SECRET_ACCESS_KEY,
            settings.AMAZON_ASSOCIATES_TRACKING_ID,
            Parser=xmltodict.parse
        )

    def _request_combined_data(self, asin):
        """Request combined attributes and listing information for an item.

        Args:
            asin (str): An item's ASIN

        Returns:
            dict: The API response

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If the request errored out
        """
        with raise_throttling_exception():
            response = self.connect().ItemLookup(ItemId=asin, ResponseGroup='ItemAttributes,Variations')

        return self._validate_response(response, asin)

    def _extract_variations(self, item):
        """Extract a list of item variations from an item's details.

        Args:
            item (dict): An item's details from a parsed API response

        Returns:
            list: All item variations
        """
        variations = item['Variations']['Item']

        if isinstance(variations, OrderedDict):
            variations = [variations]

        return variations

    def _calculate_price(self, variations):
        """Calculate the average price for the item based on all offers.

        Args:
            variations (list): A list of all item variations

        Returns:
            decimal.Decimal: The average price
        """
        total_price = 0

        for variation in variations:
            if 'Offers' in variation:
                price = variation['Offers']['Offer']['OfferListing']['Price']['Amount']
                total_price += int(price)

        avg_price = total_price / len(variations)
        return Decimal('%.02f' % (avg_price / 100))

    def _find_colors(self, variations):
        """Find the names of all colors in which the item is available.

        Args:
            variations (list): A list of all item variations

        Returns:
            list: The names of all colors
        """
        colors = set()

        for variation in variations:
            if 'ItemAttributes' in variation:
                color = variation['ItemAttributes'].get('Color', None)
                if color:
                    colors.add(color)

        return sorted(colors)

    def _find_images(self, item, size_names):
        """Find all images for an item matching a list of sizes.

        Args:
            item (dict): An item's details
            size_names (list): A list of all valid size names

        Returns:
            list: The URLs of all images
        """
        images = []

        for variation in item['Variations']['Item']:
            for size_name in size_names:
                if size_name in variation:
                    images.append(variation[size_name])

        return [image['URL'] for image in images]

    def _find_color_image(self, variations, size_name, color_names):
        """Find an image of a given size for an item of a given color.

        If no explicit image of the item in the given color can be found, this
        will fall back to using the generic product image.

        Args:
            variations (list): A list of all item variations
            size_name (str): The name of the image size to use
            color_names (list): The names of the colors to search for

        Returns:
            str: The URL of the image
        """
        image = None

        color_images = {}
        color_matches = [cn.lower() for cn in color_names]

        if color_matches:
            for variation in variations:
                if size_name not in variation:
                    continue
                color_name = variation['ItemAttributes']['Color'].lower()
                if color_name in color_matches:
                    color_images[color_name] = variation[size_name]

        for color_match in color_matches:
            image = color_images.get(color_match, None)
            if image:
                break

        if image is None:
            for variation in variations:
                if size_name in variation:
                    image = variation[size_name]
                    break

        return image['URL']

    def _validate_response(self, response, asin):
        """Raise a lookup error if a response is invalid.

        Args:
            response (dict): A response to a lookup request
            asin (str): The ASIN of the requested item

        Returns:
            dict: A validated response

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If the request errored out
        """
        lookup = response['ItemLookupResponse']
        errors = lookup['Items']['Request'].get('Errors')
        if errors:
            error = errors['Error']
            raise LookupError('Invalid lookup for ASIN %s: %s (%s)' % (
                asin, error['Code'], error['Message']))

        return lookup
