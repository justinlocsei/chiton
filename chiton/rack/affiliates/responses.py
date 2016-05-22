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


def SizeNumber():
    def validator(v):
        if v < 0:
            raise ValueError('Sizes cannot be negative')
    return validator


class ItemAvailability:
    """Details of an item's availability in a particular size."""

    VARIANT_FIELDS = ('is_petite', 'is_plus_sized', 'is_regular', 'is_tall')

    SCHEMA = V.Schema({
        'is_petite': bool,
        'is_plus_sized': bool,
        'is_regular': bool,
        'is_tall': bool,
        V.Required('size'): V.All(int, SizeNumber())
    })

    def __init__(self, is_petite=False, is_plus_sized=False, is_regular=False, is_tall=False, size=None):
        """Create a record of an item's availability.

        Keyword Args:
            is_petite (bool): Whether the availability is for the tall variant
            is_plus_sized (bool): Whether the availability is for plus sizes
            is_regular (bool): Whether the availability is for regular sizes
            is_tall (bool): Whether the availability is for the short variant
            size (str): The name of the item's size
        """
        data = {
            'is_petite': is_petite,
            'is_plus_sized': is_plus_sized,
            'is_regular': is_regular,
            'is_tall': is_tall,
            'size': size
        }

        try:
            self.SCHEMA(data)
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        variants = [data.get(f) for f in self.VARIANT_FIELDS]
        if len([v for v in variants if v]) != 1:
            raise ConfigurationError('A single variant type must be selected')

        self.is_petite = is_petite
        self.is_plus_sized = is_plus_sized
        self.is_regular = is_regular
        self.is_tall = is_tall
        self.size = size


class ItemDetails:
    """Details of an affiliate item returned by its API."""

    SCHEMA = V.Schema({
        V.Required('availability'): [ItemAvailability.SCHEMA, bool],
        V.Required('image'): ItemImage.SCHEMA,
        V.Required('name'): V.All(str, V.Length(min=1)),
        V.Required('price'): Decimal,
        V.Required('thumbnail'): ItemImage.SCHEMA
    })

    def __init__(self, availability=None, image=None, name=None, price=None, thumbnail=None):
        """Create item details.

        Keyword Args:
            availability (bool,list): Availability information for the item
            image (dict): Information on the item's primary image
            name (str): The name of the item
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
                'name': name,
                'price': price,
                'thumbnail': thumbnail
            })
        except V.MultipleInvalid as e:
            raise ConfigurationError(e)

        self.image = ItemImage(**image)
        self.name = name
        self.price = price
        self.thumbnail = ItemImage(**thumbnail)

        if isinstance(availability, bool):
            self.availability = availability
        else:
            self.availability = [ItemAvailability(**a) for a in availability]
