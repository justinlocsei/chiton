import voluptuous as V

from chiton.core.exceptions import FormatError


def define_data_shape(schema, defaults=None):
    """Create a function that validates a dict according to a schema.

    If the dict given to the generated function is valid, it will be returned
    without modifications.

    Args:
        schema (dict): A Voluptuous schema

    Keyword Args:
        defaults (dict): Default values to apply to the input

    Returns:
        function: A function that creates and validates a dict according to the schema
    """
    def validate(data={}):
        if defaults:
            base = defaults.copy()
            base.update(data)
            data = base

        try:
            V.Schema(schema)(data)
        except V.MultipleInvalid as e:
            raise FormatError('Invalid data format: %s' % e)
        else:
            return data

    return validate


def OneOf(choices):
    """A Voluptuous validator that ensure that a value is found in a choice list.

    Args:
        choices (list): The list of valid choices

    Returns:
        function: The validator function
    """
    def validator(v):
        if v not in choices:
            raise ValueError('%s must be one of "%s"' % (v, ', '.join([str(c) for c in choices])))

    return validator
