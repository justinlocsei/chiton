def build_choice_weights_lookup(choice_labels, choices, max_weight=1.0):
    """Create a lookup table mapping choice names to their weight.

    Args:
        choice_labels (list): An list of choice labels, in ascending order of importance
        choices (dict): A mapping between internal choice labels and their values

    Keyword Args:
        max_weight (float): The maximum weight value

    Returns:
        dict: A lookup mapping choice names to their weights
    """
    lookup = {}

    total_choices = len(choice_labels) - 1
    for i, choice_name in enumerate(choice_labels):
        choice_weight = i / total_choices if total_choices else 0
        lookup[choices[choice_name]] = choice_weight * max_weight

    return lookup
