from contextlib import contextmanager
from functools import partial


class PipelineProfile:
    """A value object that represents a profile for user in a pipeline."""

    def __init__(self, age=None, body_shape=None, expectations={}, styles=[]):
        """Create a new pipeline profile.

        Keyword Args:
            age (int): The age of the user
            body_shape (str): The identifier for the user's body shape
            expectations (dict): A dict mapping formality slugs to frequency identifiers
            styles (list): A list of the slugs of all target styles
        """
        self.age = age
        self.body_shape = body_shape
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
            key (str): A dot-separated namespace for the log message
            message (*): Any Python data type that describes the message
        """
        debug_log = self._debug_log

        levels = key.split('.')
        for level in levels[:-1]:
            debug_log.setdefault(level, {})
            debug_log = debug_log[level]

        target = levels.pop()
        debug_log.setdefault(target, [])
        debug_log[target].append(message)

    @property
    def debug_log(self):
        """The debug log.

        Returns:
            dict: A series of namespaced messages
        """
        return self._debug_log

    def get_debug_messages(self, key):
        """Return the debug messages associated with a given log key.

        Args:
            key (str): The log key

        Returns:
            list: All log messages for the key
        """
        debug_log = self._debug_log

        levels = key.split('.')
        for level in levels[:-1]:
            debug_log = debug_log.get(level, None)
            if debug_log is None:
                return []

        return debug_log.get(levels.pop(), [])

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
            function: A partial apply function that includes the
        """
        profile_data = self.provide_profile_data(profile)
        yield partial(self.apply, **profile_data)

    def apply(self, *args, **kwargs):
        """Allow a child step to apply its logic to an input.

        This method will receive any data returned from `provide_profile_data`
        as additional keyword args.
        """
        raise NotImplementedError
