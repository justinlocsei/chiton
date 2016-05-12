from chiton.rack.affiliates.exceptions import ConfigurationError, LookupError
from chiton.rack.affiliates.responses import ItemDetails, ItemOverview


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
            return ItemOverview(**data)
        except ConfigurationError as e:
            raise LookupError('Incorrect overview format: %s' % e)

    def request_details(self, guid, color=None):
        """Request detailed information on an item.

        Args:
            guid (str): The item's unique ID

        Keyword Args:
            color (str): The item's color

        Returns:
            chiton.rack.affiliates.responses.ItemDetails: Details on the item

        Raises:
            chiton.rack.afiliates.exceptions.LookupError: If details could not be returned
        """
        data = self.provide_details(guid, color)

        try:
            return ItemDetails(**data)
        except ConfigurationError as e:
            raise LookupError('Incorrect details format: %s' % e)

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

        The returned dict should provide the following information:

            name - The name of the item
            guid - The GUID of the item

        Args:
            url (str): The item's URL

        Returns:
            dict: Information on the item's overview
        """
        raise NotImplementedError()

    def provide_details(self, guid, color):
        """Allow a child affiliate to return an item's details.

        The returned dict should provide the following information:

            availability - An optional list of availability details
            image        - Information on the item's primary image
            price        - A decimal of the item's price
            thumbnail    - Information on the item's thumbnail image

        Args:
            guid (str): The item's GUID
            color (str): The name of the item's color

        Returns:
            dict: Information on the item's overview
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
