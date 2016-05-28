from chiton.wintour.pipeline import PipelineStep


class BaseWeight(PipelineStep):
    """The base class for all weights."""

    def configure(self, importance=1, **kwargs):
        """Create a new weight.

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
        """Log a message explaining why a weight was applied to a garment.

        Args:
            garment (chiton.closet.models.Garment): A garment instance
            weight (float): The weight applied
            reason (str): The reason the weight was applied
        """
        self.log(self._make_garment_log_key(garment), {
            'reason': reason,
            'weight': weight
        })

    def get_explanations(self, garment):
        """Return a list of all weight explanations for a garment.

        Args:
            garment (chiton.closet.models.Garment): A garment instance

        Returns:
            list: A list of dicts describing the garment's applied weights
        """
        return self.get_log_messages(self._make_garment_log_key(garment))

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

    def _make_garment_log_key(self, garment):
        """Determine the log key for a garment.

        Args:
            garment (chiton.closet.models.Garment): A garment instance

        Returns:
            str: The garment's log key
        """
        return 'garments.%s' % garment.pk
