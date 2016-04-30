class BaseFilter:
    """The class for all filters."""

    def __init__(self, profile):
        """Create a filter instance for a wardrobe profile.

        Args:
            profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile
        """
        self.profile = profile

    def apply(self, garments):
        """Apply the filter to a set of garments.

        Args:
            garments (django.db.models.query.QuerySet): A queryset of garments

        Returns:
            django.db.models.query.QuerySet: The filtered garments
        """
        return garments
