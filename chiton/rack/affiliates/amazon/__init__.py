import bottlenose
from django.conf import settings
import xmltodict

from chiton.rack.affiliates.amazon.urls import extract_asin_from_url
from chiton.rack.affiliates.base import Affiliate as BaseAffiliate
from chiton.rack.affiliates.exceptions import LookupError


class Affiliate(BaseAffiliate):
    """An affiliate for Amazon Associates."""

    def configure(self):
        self._connection = None

    def request_overview(self, url):
        asin = extract_asin_from_url(url)
        if asin is None:
            raise LookupError('No ASIN could be extracted from the URL %s' % url)

        connection = self._connect()
        response = connection.ItemLookup(ItemId=asin, ResponseGroup='Small')
        validated = self._validate_response(response['ItemLookupResponse'], asin)

        item = validated['Items']['Item']
        name = item.get('ItemAttributes', {}).get('Title')

        return {
            'guid': item['ASIN'],
            'name': name
        }

    def _connect(self):
        """Return a connection to the Product Advertising API.

        Returns:
            bottlenose.Amazon: A connection to the API
        """
        if not self._connection:
            self._connection = bottlenose.Amazon(
                settings.AWS_ADVERTISING_ACCESS_KEY_ID,
                settings.AWS_ADVERTISING_SECRET_ACCESS_KEY,
                settings.AWS_ADVERTISING_ASSOCIATE_TAG,
                Parser=xmltodict.parse)

        return self._connection

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
        errors = response['Items']['Request'].get('Errors')
        if errors:
            error = errors['Error']
            raise LookupError('Invalid lookup for ASIN %s: %s (%s)' % (
                asin, error['Code'], error['Message']))

        return response
