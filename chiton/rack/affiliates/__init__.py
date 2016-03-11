from django.utils.module_loading import import_string


def create_affiliate(slug):
    """Create an Affiliate class instance from an affiliate slug.

    Args:
        slug (str): The slug of an affiliate

    Returns:
        chiton.rack.affiliates.base.Affiliate: The affiliate class

    Raises:
        ImportError: If the requested affiliate does not exist
    """
    Affiliate = import_string('chiton.rack.affiliates.%s.Affiliate' % slug)
    return Affiliate()
