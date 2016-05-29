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
