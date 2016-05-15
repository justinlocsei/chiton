import bottlenose
from decimal import Decimal
from django.conf import settings
import xmltodict

from chiton.rack.affiliates.amazon.urls import extract_asin_from_url
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate
from chiton.rack.affiliates.exceptions import LookupError


class Affiliate(BaseAffiliate):
    """An affiliate for Amazon Associates."""

    def configure(self):
        self._connection = None

    def provide_overview(self, url):
        asin = extract_asin_from_url(url)
        if asin is None:
            raise LookupError('No ASIN could be extracted from the URL: %s' % url)

        connection = self._connect()
        response = connection.ItemLookup(ItemId=asin, ResponseGroup='Small')
        validated = self._validate_response(response, asin)

        item = validated['Items']['Item']
        name = item.get('ItemAttributes', {}).get('Title')

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

        price = self._calculate_price(item['Variations']['Item'])
        image = self._find_image(item, 'LargeImage', colors)
        thumbnail = self._find_image(item, 'MediumImage', colors)

        return {
            'availability': True,
            'image': image,
            'price': price,
            'thumbnail': thumbnail
        }

    def provide_raw(self, asin):
        data = self._request_combined_data(asin)
        return data['Items']

    def _connect(self):
        """Return a connection to the Amazon Associates API.

        Returns:
            bottlenose.Amazon: A connection to the API
        """
        if not self._connection:
            self._connection = bottlenose.Amazon(
                settings.AMAZON_ASSOCIATES_AWS_ACCESS_KEY_ID,
                settings.AMAZON_ASSOCIATES_AWS_SECRET_ACCESS_KEY,
                settings.AMAZON_ASSOCIATES_TRACKING_ID,
                Parser=xmltodict.parse)

        return self._connection

    def _request_combined_data(self, asin):
        """Request combined attributes and listing information for an item.

        Args:
            asin (str): An item's ASIN

        Returns:
            dict: The API response

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If the request errored out
        """
        connection = self._connect()
        response = connection.ItemLookup(ItemId=asin, ResponseGroup='ItemAttributes,Variations')
        return self._validate_response(response, asin)

    def _calculate_price(self, variations):
        """Calculate the average price for the item based on all offers.

        Args:
            variations (dict): A list of all item variations

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
        variations = parsed['Variations']['Item']

        color_images = {}
        color_matches = [cn.lower() for cn in color_names]

        if color_matches:
            for variation in variations:
                color_name = variation['ItemAttributes']['Color'].lower()
                if color_name in color_matches:
                    color_images[color_name] = variation[size_name]

        for color_match in color_matches:
            image = color_images.get(color_match, None)
            if image:
                break

        if image is None:
            image = variations[0][size_name]

        return {
            'height': int(image['Height']['#text']),
            'url': image['URL'],
            'width': int(image['Width']['#text'])
        }

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
            if isinstance(error, list):
                error = error[0]
            raise LookupError('Invalid lookup for ASIN %s: %s (%s)' % (
                asin, error['Code'], error['Message']))

        return lookup
