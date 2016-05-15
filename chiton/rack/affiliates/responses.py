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


class ItemImage:
    """A description of an item's image."""

    SCHEMA = V.Schema({
        V.Required('height'): int,
        V.Required('url'): V.All(str, V.Length(min=1)),
        V.Required('width'): int
    })

    def __init__(self, height=None, url=None, width=None):
        """Create an item image.

        Keyword Args:
            height (int): The height of the image in pixels
            url (str): The absolute URL for the image
            width (int): The width of the image in pixels
        """
        try:
            self.SCHEMA({
                'height': height,
                'url': url,
                'width': width
            })
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        self.height = height
        self.url = url
        self.width = width


class ItemAvailability:
    """Details of an item's availability in a particular size."""

    SCHEMA = V.Schema({
        V.Required('size'): V.All(str, V.Length(min=1))
    })

    def __init__(self, size=None):
        """Create a record of an item's availability.

        Keyword Args:
            size (str): The name of the item's size
        """
        try:
            self.SCHEMA({
                'size': size
            })
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        self.size = size


class ItemDetails:
    """Details of an affiliate item returned by its API."""

    SCHEMA = V.Schema({
        V.Required('availability'): [ItemAvailability.SCHEMA, bool],
        V.Required('image'): ItemImage.SCHEMA,
        V.Required('price'): Decimal,
        V.Required('thumbnail'): ItemImage.SCHEMA
    })

    def __init__(self, availability=None, image=None, price=None, thumbnail=None):
        """Create item details.

        Keyword Args:
            availability (bool,list): Availability information for the item
            image (dict): Information on the item's primary image
            price (decimal.Decimal): The price for the item
            thumbnail (dict): Information on the item's thumbnail image
        """
        if isinstance(availability, bool):
            check_availability = [availability]
        else:
            check_availability = availability

        try:
            self.SCHEMA({
                'availability': check_availability,
                'image': image,
                'price': price,
                'thumbnail': thumbnail
            })
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        self.image = ItemImage(**image)
        self.price = price
        self.thumbnail = ItemImage(**thumbnail)

        if isinstance(availability, bool):
            self.availability = availability
        else:
            self.availability = [ItemAvailability(size=a['size']) for a in availability]
