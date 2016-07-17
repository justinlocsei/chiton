from contextlib import contextmanager
from functools import partial

import voluptuous as V

from chiton.core.schema import define_data_shape


DebugExplanations = define_data_shape({
    V.Required('weights'): [{
        V.Required('name'): str,
        V.Required('reasons'): [{
            V.Required('reason'): str,
            V.Required('weight'): V.Any(float, int)
        }]
    }],
    V.Required('normalization'): [{
        V.Required('importance'): V.Any(float, int),
        V.Required('name'): str,
        V.Required('weight'): V.Any(float, int)
    }]
}, validated=False)


ProductImage = define_data_shape({
    V.Required('height'): int,
    V.Required('relative_url'): str,
    V.Required('width'): int
}, validated=False)


PurchaseOption = define_data_shape({
    V.Required('id'): int,
    V.Required('images'): [ProductImage],
    V.Required('network_name'): str,
    V.Required('price'): V.Any(None, int),
    V.Required('retailer'): str,
    V.Required('url'): str
}, validated=False)


GarmentOverview = define_data_shape({
    V.Required('brand'): str,
    V.Required('branded_name'): str,
    V.Required('id'): int,
    V.Required('name'): str
}, validated=False)


GarmentRecommendation = define_data_shape({
    'explanations': DebugExplanations,
    V.Required('garment'): GarmentOverview,
    V.Required('purchase_options'): [PurchaseOption],
    V.Required('weight'): V.Any(float, int)
}, validated=False)


BasicOverview = define_data_shape({
    V.Required('category'): str,
    V.Required('id'): int,
    V.Required('name'): str,
    V.Required('slug'): str
}, validated=False)


FacetGroup = define_data_shape({
    V.Required('garment_ids'): [int],
    V.Required('slug'): str
}, validated=False)


Facet = define_data_shape({
    V.Required('name'): str,
    V.Required('groups'): [FacetGroup],
    V.Required('slug'): str
}, validated=False)


BasicRecommendations = define_data_shape({
    V.Required('basic'): BasicOverview,
    V.Required('facets'): [Facet],
    V.Required('garments'): [GarmentRecommendation]
}, validated=False)


Recommendations = define_data_shape({
    V.Required('basics'): [BasicRecommendations],
    'debug': {
        V.Required('queries'): [{
            V.Required('time'): float,
            V.Required('sql'): str
        }],
        V.Required('time'): float
    }
}, validated=False)


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
            profile (chiton.wintour.profiles.PipelineProfile): A wardrobe profile

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
            profile (chiton.wintour.profiles.PipelineProfile): A wardrobe profile

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
