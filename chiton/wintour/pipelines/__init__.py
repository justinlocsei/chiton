from operator import itemgetter

from chiton.closet.models import Garment


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
        garments = self.provide_garments()
        facets = [facet_class() for facet_class in self.provide_facets()]

        # Apply all filters to the set of garments
        for filter_class in self.provide_filters():
            filter_instance = filter_class(profile)
            garments = filter_instance.apply(garments)

        # Apply each weight to each garment, and group the results by weight,
        # while keeping data on the weight's value ranges and importance
        weightings = {}
        for pipeline_weight in self.provide_weights():
            weight = pipeline_weight.weight(profile)
            weighted_garments = []
            max_weight = 0
            min_weight = 0

            for garment in garments:
                applied_weight = weight.apply(garment)
                weighted_garments.append({
                    'garment': garment,
                    'weight': applied_weight
                })

                max_weight = max(max_weight, applied_weight)
                min_weight = min(min_weight, applied_weight)

            weightings[weight] = {
                'garments': weighted_garments,
                'importance': pipeline_weight.importance,
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


class PipelineWeight:
    """A weight class wrapped for use in a pipeline."""

    def __init__(self, weight, importance=1):
        """Create a pipeline weight.

        This accepts an importance factor, which should be a positive integer
        used as a multiplier when applying the weight in the context of other
        pipeline weights.

        Args:
            weight (chiton.wintour.weights.BaseWeight): A weight class

        Keyword Args:
            importance (int): A multiplier indicating the weight's importance
        """
        self.weight = weight
        self.importance = importance
