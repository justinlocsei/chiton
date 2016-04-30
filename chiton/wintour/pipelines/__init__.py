from contextlib import contextmanager
from functools import partial
from operator import itemgetter

from chiton.closet.models import Garment


class PipelineStep:
    """An abstract base class for a step in a pipeline."""

    def __init__(self, **kwargs):
        """Create the step, and expose hooks for further configuration."""
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

    def provide_slug(self):
        """Provide the slug for the step.

        Returns:
            str: The step's slug
        """
        raise NotImplementedError

    @property
    def slug(self):
        """The step's slug.

        Returns:
            str: The slug
        """
        return self.provide_slug()


class BasePipeline:
    """The base class for all pipelines."""

    def provide_garments(self):
        """Provide the set of all garments on which to search.

        Returns:
            django.db.models.query.QuerySet: All garment models
        """
        return Garment.objects.all()

    def provide_facets(self):
        """Provide all facets for the pipeline.

        Returns:
            list: A list of all facet classes
        """
        return []

    def provide_filters(self):
        """Provide all filters for the pipeline.

        Returns:
            list: A list of all filter classes
        """
        return []

    def provide_weights(self):
        """Provide all weights for the pipeline.

        Returns:
            list: A list of all weight classes
        """
        return []

    def make_recommendations(self, profile):
        """Make recommendations for a wardrobe profile.

        The recommendations are exposed as a dict keyed by Basic model
        instances, whose subkeys provide facets grouping Garment instances with
        metadata indicating the strength of the match for the profile.

        Args:
            profile (chiton.wintour.models.WardrobeProfile): A wardrobe profile

        Returns:
            dict: The recommendations
        """
        garments = self.provide_garments().select_related('basic')

        filters = self.provide_filters()
        facets = self.provide_facets()
        weights = self.provide_weights()

        # Apply all filters to the set of garments
        for filter_instance in filters:
            with filter_instance.apply_to_profile(profile) as filter_function:
                garments = filter_function(garments)

        # Apply each weight to each garment, and group the results by weight,
        # while keeping data on the weight's value ranges and importance
        weightings = {}
        for weight in weights:
            weighted_garments = []
            max_weight = 0
            min_weight = 0

            with weight.apply_to_profile(profile) as weight_function:
                for garment in garments:
                    applied_weight = weight_function(garment)
                    weighted_garments.append({
                        'garment': garment,
                        'weight': applied_weight
                    })
                    max_weight = max(max_weight, applied_weight)
                    min_weight = min(min_weight, applied_weight)

            weightings[weight] = {
                'garments': weighted_garments,
                'importance': weight.importance,
                'max': max_weight,
                'min': min_weight
            }

        # Build a master list of weighted garments by combining the weight
        # values applied to each garment and using each weight's importance to
        # determine the final applied weight
        weighted_garments = {}
        for weight, values in weightings.items():
            for weighted_garment in values['garments']:
                garment = weighted_garment['garment']
                weighted_garments.setdefault(garment, 0)
                weighted_garments[garment] += weighted_garment['weight']

        # Group garments by their basic type
        by_basic = {}
        for garment, weight in weighted_garments.items():
            by_basic.setdefault(garment.basic, [])
            by_basic[garment.basic].append({
                'garment': garment,
                'weight': weight
            })

        # Generate faceted recommendations grouped by basic type
        recs = {}
        weight_fetcher = itemgetter('weight')
        for basic, weighted_garments in by_basic.items():
            sorted_garments = sorted(weighted_garments, key=weight_fetcher, reverse=True)

            faceted = {}
            for facet in facets:
                faceted[facet] = facet.apply(sorted_garments)

            recs[basic] = {
                'facets': faceted,
                'garments': sorted_garments
            }

        return recs
