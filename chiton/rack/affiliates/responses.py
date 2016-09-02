from decimal import Decimal

import voluptuous as V

from chiton.core.schema import define_data_shape


def _SizeNumber():
    """A validator that ensures that a size is a positive number."""
    def validator(v):
        if v < 0:
            raise V.Invalid('Sizes cannot be negative')
    return validator


# Details of an item's availability in a particular size
ItemAvailability = define_data_shape({
    'is_petite': bool,
    'is_plus_sized': bool,
    'is_regular': bool,
    'is_tall': bool,
    V.Required('size'): V.All(int, _SizeNumber())
}, {
    'is_petite': False,
    'is_plus_sized': False,
    'is_regular': False,
    'is_tall': False
})


# A high-level overview of an item
ItemOverview = define_data_shape({
    V.Required('guid'): V.All(str, V.Length(min=1)),
    V.Required('name'): V.All(str, V.Length(min=1))
})


# Details of an affiliate item returned by its API
ItemDetails = define_data_shape({
    V.Required('availability'): V.Any([ItemAvailability], bool),
    V.Required('images'): [str],
    V.Required('name'): V.All(str, V.Length(min=1)),
    V.Required('price'): Decimal,
    V.Required('retailer'): str,
    V.Required('url'): str
})
