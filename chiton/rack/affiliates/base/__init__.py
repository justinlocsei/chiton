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

    def provide_overview(self, url):
        """Allow a child affiliate to return an item's overview.

        Args:
            url (str): The item's URL

        Returns:
            dict: A dictionary with the overview data
        """
        raise NotImplementedError()

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
