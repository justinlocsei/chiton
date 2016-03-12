from django.utils.module_loading import import_string


def create_affiliate(slug=None):
    """Create an Affiliate class instance appropriate for the input.

    Keyword Args:
        slug (str): The slug for the affiliate

    Returns:
        chiton.rack.affiliates.base.Affiliate: The affiliate class

    Raises:
        ImportError: If the requested affiliate does not exist
    """
    Affiliate = import_string('chiton.rack.affiliates.%s.Affiliate' % slug)
    return Affiliate()
