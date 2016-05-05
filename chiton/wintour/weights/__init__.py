from chiton.wintour.pipeline import PipelineStep


def _make_garment_namespace(garment):
    """Create a logging namespace for a garment.

    Args:
        garment (chiton.closet.models.Garment): A garment instance

    Returns:
        str: The garment's namespace
    """
    return 'garments.%s' % garment.pk


class BaseWeight(PipelineStep):
    """The base class for all weights."""

    def configure(self, importance=1, **kwargs):
        """Track the importance factor for the weight.

        The importance factor should be a positive integer used as a multiplier
        when applying the weight in the context of other pipeline weights.

        Keyword Args:
            importance (int): A multiplier indicating the weight's importance
        """
        self.importance = importance
        self.configure_weight(**kwargs)

    def configure_weight(self, **kwargs):
        """Allow a child weight to perform custom configuration."""
        pass

    def explain_weight(self, garment, weight, reason):
        """Log a message describing a weight applied to a garment.

        Args:
            garment (chiton.closet.models.Garment): A garment instance
            weight (float): The weight applied
            reason (str): The reason the weight was applied
        """
        self.log(_make_garment_namespace(garment), {
            'reason': reason,
            'weight': weight
        })

    def get_explanations(self, garment):
        """Return a list of all weight explanations for a garment.

        Args:
            garment (chiton.closet.models.Garment): A garment instance

        Returns:
            list: A list of dicts describing the garment's weights
        """
        return self.get_debug_messages(_make_garment_namespace(garment))

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
