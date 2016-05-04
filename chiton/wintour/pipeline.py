from contextlib import contextmanager
from functools import partial


class PipelineStep:
    """An abstract base class for a step in a pipeline."""

    name = None
    slug = None

    def __init__(self, **kwargs):
        """Create the step, and expose hooks for further configuration."""
        if self.name is None:
            raise NotImplementedError('Pipeline steps must define a name attribute')

        if self.slug is None:
            raise NotImplementedError('Pipeline steps must define a slug attribute')

        self.configure(**kwargs)

    def configure(self, **kwargs):
        """Allow a child class to perform custom configuration."""
        pass

    def provide_profile_data(self, profile):
        """Provide a data structure of important information from the profile.

        This is used by child classes to pre-calculate and parse a profile
        instance before using it to apply logic to a set of garments.  This
        value should return a dict, which will be used to provide additional
        keyword args to any `apply` calls in the profile's context.

        Args:
            profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

        Returns:
            dict: Additional keyword args to pass to apply calls
        """
        return {}

    def prepare_garments(self, garments):
        """Allow a child to modify a queryset of garments before operations.

        This can be used to add prefetched or selected fields to the garments,
        for example, in cases where the step requires nested data.

        Args:
            garments (django.db.models.query.QuerySet): A queryset of garments

        Returns:
            django.db.models.query.QuerySet: The modified set of garments
        """
        return garments

    @contextmanager
    def apply_to_profile(self, profile):
        """Provide a context in which the pipeline step acts on a profile.

        Args:
            profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

        Yields:
            function: A partial apply function that includes the
        """
        profile_data = self.provide_profile_data(profile)
        yield partial(self.apply, **profile_data)

    def apply(self, *args, **kwargs):
        """Allow a child class to apply its logic to an input.

        This method will receive any data returned from `provide_profile_data`
        as additional keyword args.
        """
        raise NotImplementedError

