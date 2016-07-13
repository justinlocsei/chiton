import re

# A list of text transforms to apply to a formatted floating-point value
FLOAT_TRANSFORMS = (
    re.compile(r'\.0+$'),
    re.compile(r'\.$')
)


def format_float(value, precision=2):
    """Format a floating-point number as a string with aribtrary precision.

    This gets the number as close as possible to an integer by removing any
    trailing zeroes and unnecessary periods.

    Args:
        value (float): A floating-point value

    Keyword Args:
        precision (int): The number of decimal places to show

    Returns:
        str: The formatted number
    """
    formatting = '%0.' + str(precision) + 'f'
    formatted = formatting % value

    for transform in FLOAT_TRANSFORMS:
        formatted = re.sub(transform, '', formatted)

    return formatted


def price_to_integer(price):
    """Convert a price to an integer representing its value in cents.

    Params:
        price (decimal.Decimal): A price as a decimal

    Returns:
        int: The price as an integer in cents
    """
    return int(float(price) * 100) if price is not None else None
