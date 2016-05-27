from chiton.wintour.pipeline import PipelineStep


class BaseGarmentFilter(PipelineStep):
    """The base class for all filters."""

    def apply(self, garment):
        """Decide whether to exclude a single garment.

        Args:
            garment (chiton.closet.models.Garment): A single garment

        Returns:
            bool: Whether to exclude the garment
        """
        return False
