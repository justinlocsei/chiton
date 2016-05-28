from contextlib import contextmanager
from functools import partial


class PipelineProfile:
    """A value object that represents a profile for user in a pipeline."""

    def __init__(self, age=None, avoid_care=[], body_shape=None, expectations={}, sizes=[], styles=[]):
        """Create a new pipeline profile.

        Keyword Args:
            age (int): The age of the user
            avoid_care (list): Identifiers for care instructions to avoid
            body_shape (str): The identifier for the user's body shape
            expectations (dict): A dict mapping formality slugs to frequency identifiers
            size (list): A list of the slugs of all target sizes
            styles (list): A list of the slugs of all target styles
        """
        self.age = age
        self.avoid_care = avoid_care
        self.body_shape = body_shape
        self.sizes = sizes
        self.styles = styles
        self.expectations = expectations


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

        self.debug = False
        self._debug_log = {}

        self.configure(**kwargs)

    def configure(self, **kwargs):
        """Allow a child step to perform custom configuration."""
        pass

    def log(self, key, message):
        """Add a message to the debug log.

        Args:
            key (str): A namespace for the log message
            message (*): Any Python data type that describes the message
        """
        self._debug_log.setdefault(key, [])
        self._debug_log[key].append(message)

    def get_log_messages(self, key):
        """Return the log messages associated with a given log key.

        Args:
            key (str): The log key

        Returns:
            list: All log messages for the key
        """
        return self._debug_log.get(key, [])

    def provide_profile_data(self, profile):
        """Provide a data structure of important information from the profile.

        This is used by child classes to pre-calculate and parse a profile
        instance before using it to apply logic to a set of garments.  This
        value should return a dict, which will be used to provide additional
        keyword args to any `apply` calls in the profile's context.

        Args:
            profile (chiton.wintour.pipeline.PipelineProfile): A wardrobe profile

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

        This yields a partial version of the `apply` function that will be
        called with the keyword args prepared by the current pipeline step from
        the profile.

        Args:
            profile (chiton.wintour.pipeline.PipelineProfile): A wardrobe profile

        Yields:
            function: A partially apply function that includes the profile data
        """
        profile_data = self.provide_profile_data(profile)
        yield partial(self.apply, **profile_data)

    def apply(self, *args, **kwargs):
        """Allow a child step to apply its logic to an input.

        This method will receive any data returned from `provide_profile_data`
        as additional keyword args.
        """
        raise NotImplementedError
