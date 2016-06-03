from chiton.core.exceptions import FormatError
from chiton.rack.affiliates.exceptions import LookupError
from chiton.rack.affiliates.responses import ItemAvailability, ItemDetails, ItemOverview


class Affiliate:
    """The base class for all affiliates."""

    def __init__(self):
        """Initialize the affiliate."""
        self.configure()

    def configure(self):
        """Allow a child affiliate to perform initial configuration."""
        pass

    def request_overview(self, url):
        """Request a high-level overview of the item.

        Args:
            url (str): The item's URL

        Returns:
            chiton.rack.affiliates.responses.ItemOverview: An overview of the item

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If an overview could not be returned
        """
        data = self.provide_overview(url)

        try:
            return ItemOverview(data)
        except FormatError as e:
            raise LookupError('Incorrect overview format: %s' % e)

    def request_details(self, guid, colors=[]):
        """Request detailed information on an item.

        Args:
            guid (str): The item's unique ID

        Keyword Args:
            colors (list): The names of all colors for the item

        Returns:
            chiton.rack.affiliates.responses.ItemDetails: Details on the item

        Raises:
            chiton.rack.afiliates.exceptions.LookupError: If details could not be returned
        """
        data = self.provide_details(guid, colors)

        try:
            details = ItemDetails(data)
        except FormatError as e:
            raise LookupError('Incorrect details format: %s' % e)

        if not isinstance(details['availability'], bool) and details['availability']:
            details['availability'] = [ItemAvailability(a) for a in details['availability']]

        return details

    def request_raw(self, guid):
        """Request the raw API response for an item.

        Args:
            guid (str): The item's unique ID

        Returns:
            dict: The raw API response for the item

        Raises:
            chiton.rack.afiliates.exceptions.LookupError: If the response was unsuccessful
        """
        raw = self.provide_raw(guid)

        if not isinstance(raw, dict):
            raise LookupError('API responses must be returned as dict')

        return raw

    def provide_overview(self, url):
        """Allow a child affiliate to return an item's overview.

        Args:
            url (str): The item's URL

        Returns:
            chiton.rack.affiliates.responses.ItemOverview: Information on the item's overview
        """
        raise NotImplementedError()

    def provide_details(self, guid, colors):
        """Allow a child affiliate to return an item's details.

        Args:
            guid (str): The item's GUID
            colors (list): The names of the item's colors

        Returns:
            chiton.rack.affiliates.responses.ItemDetails: Information on the item's overview
        """
        raise NotImplementedError()

    def provide_raw(self, guid):
        """Allow a child affiliate to return a raw API response.

        Args:
            guid (str): The item's GUID

        Returns:
            dict: The raw API response data
        """
        raise NotImplementedError()
