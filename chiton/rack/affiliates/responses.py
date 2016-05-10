from decimal import Decimal

import voluptuous as V

from chiton.rack.affiliates.exceptions import ConfigurationError


class ItemOverview:
    """An overview of an affiliate item returned by its API."""

    SCHEMA = V.Schema({
        V.Required('guid'): V.All(str, V.Length(min=1)),
        V.Required('name'): V.All(str, V.Length(min=1))
    })

    def __init__(self, guid=None, name=None):
        """Create an item overview.

        Keyword Args:
            guid (str): The item's GUID
            name (str): The item's name

        Raises:
            chiton.rack.affiliates.exceptions.LookupError: If any required fields are missing
        """
        try:
            self.SCHEMA({
                'guid': guid,
                'name': name
            })
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        self.guid = guid
        self.name = name


class ItemDetails:
    """Details of an affiliate item returned by its API."""

    SCHEMA = V.Schema({
        V.Required('price'): Decimal
    })

    def __init__(self, price=None):
        """Create item details.

        Keyword Args:
            price (decimal.Decimal): The price for the item
        """
        try:
            self.SCHEMA({
                'price': price
            })
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        self.price = price
