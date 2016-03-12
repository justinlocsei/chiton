from voluptuous import All, Length, MultipleInvalid, Schema

from chiton.rack.affiliates.exceptions import LookupError


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
            dict: A dictionary with the overview data

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If an overview could not be returned
        """
        overview = self.provide_overview(url)
        return self._validate_overview(overview)

    def request_details(self, guid, for_display=False):
        """Request detailed information on an item.

        Args:
            guid (str): The item's unique ID

        Keyword Args:
            for_display (bool): Whether the details are being used for display purposes

        Returns:
            dict: A dictionary with the details

        Raises:
            chiton.rack.afiliates.exceptions.LookupError: If details could not be returned
        """
        if for_display:
            details = self.provide_details_for_display(guid)
        else:
            details = self.provide_details(guid)

        return self._validate_details(details)

    def provide_overview(self, url):
        """Allow a child affiliate to return an item's overview."""
        raise NotImplementedError()

    def provide_details(self, guid):
        """Allow a child affiliate to return an item's details."""
        raise NotImplementedError()

    def provide_details_for_display(self, guid):
        """Allow a child affiliate to return an item's details for display purposes."""
        return self.provide_details(guid)

    def _validate_overview(self, overview):
        """Validate an overview, raising an error if it is invalid.

        Args:
            overview (dict): An overview of an affiliate item

        Returns:
            dict: A valid overview

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If the response is invalid
        """
        schema = Schema({
            'guid': All(str, Length(min=1)),
            'name': All(str, Length(min=1))
        })

        try:
            schema(overview)
        except MultipleInvalid as e:
            raise LookupError('Invalid overview format: %s' % e)

        return overview

    def _validate_details(self, details):
        """Validate an item's details, raising an error if they are invalid.

        Args:
            details (dict): Details about an affiliate item

        Returns:
            dict: Valid details

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If the response is invalid
        """
        if not isinstance(details, dict):
            raise LookupError('Details must be provided as a dict')

        return details
