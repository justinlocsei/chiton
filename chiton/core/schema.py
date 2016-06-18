import voluptuous as V

from chiton.core.exceptions import FormatError


class DataShapeError(FormatError):
    """A custom error used when validating data shapes."""

    def __init__(self, *args, **kwargs):
        """Allow per-field errors to be provided."""
        self.fields = kwargs.pop('fields', {})
        super().__init__(*args, **kwargs)


def define_data_shape(schema, defaults=None, validated=True):
    """Create a function that validates a dict according to a schema.

    If the dict given to the generated function is valid, it will be returned
    without modifications.

    Args:
        schema (dict): A Voluptuous schema

    Keyword Args:
        defaults (dict): Default values to apply to the input
        validated (bool): Whether the data should be validated by default

    Returns:
        function: A function that creates and validates a dict according to the schema
    """
    def validate_data(data={}, validate=validated):
        if not validate:
            return data

        if defaults:
            base = defaults.copy()
            base.update(data)
            data = base

        try:
            V.Schema(schema)(data)
        except V.MultipleInvalid as e:
            field_errors = {}
            for error in e.errors:
                field_errors['.'.join([str(p) for p in error.path])] = error.msg
            raise DataShapeError(str(e), fields=field_errors)
        else:
            return data

    return validate_data


def OneOf(choices, multiple=False):
    """A Voluptuous validator that ensure that a value is in a list of choices.

    This can be called with an iterable or a function that produces an iterable.
    In the latter case, the list will be recreated during each validation.

    Args:
        choices (list, function): The list of valid choices

    Keyword Args:
        multiple (bool): Whether the value should be a single value or a list

    Returns:
        function: The validator function
    """
    def validator(v):
        if callable(choices):
            choice_list = choices()
        else:
            choice_list = choices

        choice_values = ', '.join(sorted([str(c) for c in choice_list]))

        if multiple and (not v or len(set(choice_list) & set(v)) < len(v)):
            raise V.Invalid('Only the following values are allowed: %s' % choice_values)
        elif not multiple and v not in choice_list:
            raise V.Invalid('%s is not in the following list: %s' % (str(v), choice_values))

    return validator


def NumberInRange(min_value, max_value):
    """A Voluptuous validator that ensure that a number is within a given range.

    Args:
        min_value (int): The inclusive lower bound of the range
        max_value (int): The inclusive upper bound of the range

    Returns:
        function: The validator function
    """
    def validator(v):
        if v < min_value or v > max_value:
            raise V.Invalid('%d must be between %d and %d' % (v, min_value, max_value))

    return validator
