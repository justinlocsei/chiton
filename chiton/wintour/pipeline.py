from contextlib import contextmanager
from functools import partial

import voluptuous as V

from chiton.closet.data import CARE_TYPES
from chiton.closet.models import Garment
from chiton.core.schema import define_data_shape, OneOf
from chiton.rack.models import AffiliateItem
from chiton.wintour.data import BODY_SHAPES


PipelineProfile = define_data_shape({
    V.Required('age'): int,
    V.Required('avoid_care'): list(CARE_TYPES.values()),
    V.Required('body_shape'): OneOf(BODY_SHAPES.values()),
    V.Required('expectations'): dict,
    V.Required('sizes'): [str],
    V.Required('styles'): [str]
})


FacetGroup = define_data_shape({
    V.Required('count'): int,
    V.Required('garment_ids'): [int],
    V.Required('slug'): str
}, validated=False)


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


GarmentRecommendation = define_data_shape({
    V.Required('affiliate_items'): [AffiliateItem],
    'explanations': DebugExplanations,
    V.Required('garment'): Garment,
    V.Required('weight'): V.Any(float, int)
}, validated=False)


BasicRecommendations = define_data_shape({
    V.Required('facets'): dict,
    V.Required('garments'): [GarmentRecommendation]
}, validated=False)


Recommendations = define_data_shape({
    V.Required('basics'): dict,
    'debug': {
        V.Required('queries'): [{
            V.Required('time'): float,
            V.Required('sql'): str
        }],
        V.Required('time'): float
    }
}, validated=False)


SerializedItemImage = define_data_shape({
    V.Required('height'): int,
    V.Required('url'): str,
    V.Required('width'): int
})


SerializedGarmentRecommendation = define_data_shape({
    V.Required('affiliate_items'): [{
        V.Required('id'): int,
        V.Required('image'): V.Any(SerializedItemImage, None),
        V.Required('price'): V.Any(int, None),
        V.Required('network_name'): str,
        V.Required('thumbnail'): V.Any(SerializedItemImage, None),
        V.Required('url'): str
    }],
    'explanations': DebugExplanations,
    V.Required('garment'): {
        V.Required('brand'): str,
        V.Required('id'): int,
        V.Required('name'): str
    },
    V.Required('weight'): V.Any(float, int)
}, validated=False)


SerializedBasicRecommendations = define_data_shape({
    V.Required('basic'): {
        V.Required('id'): int,
        V.Required('name'): str,
        V.Required('slug'): str
    },
    'facets': dict,
    'garments': [SerializedGarmentRecommendation]
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
