from chiton.wintour.pipelines import PipelineStep


class BaseWeight(PipelineStep):
    """The base class for all weights."""

    def configure(self, importance=1):
        """Track the importance factor for the weight.

        The importance factor should be a positive integer used as a multiplier
        when applying the weight in the context of other pipeline weights.

        Keyword Args:
            importance (int): A multiplier indicating the weight's importance
        """
        self.importance = importance

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
