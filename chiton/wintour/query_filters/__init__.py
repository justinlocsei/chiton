from chiton.wintour.pipeline import PipelineStep


class BaseQueryFilter(PipelineStep):
    """The base class for all query filters."""

    def apply(self, garments):
        """Apply the filter to a set of garments.

        Args:
            garments (django.db.models.query.QuerySet): A queryset of garments

        Returns:
            django.db.models.query.QuerySet: The filtered garments
        """
        return garments
