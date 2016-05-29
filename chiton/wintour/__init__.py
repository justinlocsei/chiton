def build_choice_weights_lookup(choices, max_weight=1.0):
    """Create a lookup table mapping choice names to their weight.

    Args:
        choices (list): A list of two-tuple choices

    Keyword Args:
        max_weight (float): The maximum weight value

    Returns:
        dict: A lookup mapping choice names to their weights
    """
    lookup = {}

    last_index = len(choices) - 1
    for i, choice in enumerate(choices):
        choice_weight = i / last_index if last_index else 1
        lookup[choice[0]] = choice_weight * max_weight

    return lookup
