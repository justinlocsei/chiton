class BaseWeight:
    """The base class for all weights."""

    def __init__(self, profile):
        """Create a weight instance for a wardrobe profile.

        Args:
            profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile
        """
        self.profile = profile

    def apply(self, garment):
        """Return the weight value to apply to a garment.

        Weight values only matter within the context of a weight.  Negative
        numbers will push an item down in the rankings, whereas positive numbers
        will push it up.

        Args:
            garment (chiton.closet.models.Garment): A garment instance

        Returns:
            int: The weight to apply to the garment
        """
        return 0
