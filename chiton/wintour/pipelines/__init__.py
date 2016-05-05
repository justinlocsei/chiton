from operator import itemgetter

from django.db import connection

from chiton.closet.models import Garment


class BasePipeline:
    """The base class for all pipelines."""

    def provide_garments(self):
        """Provide the set of all garments on which to search.

        Returns:
            django.db.models.query.QuerySet: All garment models
        """
        return Garment.objects.all()

    def load_garments(self):
        """Return the set of garments to use for the pipeline.

        Returns:
            django.db.models.query.QuerySet: All garment models
        """
        garments = self.provide_garments()

        steps = self.provide_facets() + self.provide_filters() + self.provide_weights()
        for step in steps:
            garments = step.prepare_garments(garments)

        return garments

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

    def make_recommendations(self, profile, debug=False):
        """Make recommendations for a wardrobe profile.

        The recommendations are exposed as a dict keyed by Basic model
        instances, whose subkeys provide facets grouping Garment instances with
        metadata indicating the strength of the match for the profile.

        Args:
            profile (chiton.wintour.pipeline.PipelineProfile): A wardrobe profile

        Keyword Args:
            debug (bool): Whether to generate debugging statistics

        Returns:
            dict: The recommendations
        """
        garments = self.load_garments().select_related('basic')

        filters = self.provide_filters()
        facets = self.provide_facets()
        weights = self.provide_weights()

        # Apply the given debug mode to all pipeline steps
        for step in filters + facets + weights:
            step.debug = debug

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

            weight_range = max_weight - min_weight
            if weight_range:
                for weighted_garment in weighted_garments:
                    applied_weight = weighted_garment['weight'] - min_weight
                    weighted_garment['weight'] = applied_weight / weight_range

            weightings[weight] = {
                'garments': weighted_garments,
                'importance': weight.importance
            }

        # Build a master list of weighted garments by combining the weight
        # values applied to each garment and using each weight's importance to
        # determine the final applied weight
        weighted_garments = {}
        for weight, values in weightings.items():
            for weighted_garment in values['garments']:
                garment = weighted_garment['garment']
                weighted_garments.setdefault(garment, {
                    'explanations': {},
                    'weight': 0
                })
                weighted_garments[garment]['weight'] += weighted_garment['weight'] * values['importance']

                if debug:
                    weighted_garments[garment]['explanations'][weight.slug] = weight.get_explanations(garment)

        # Group garments by their basic type
        max_weight = 0
        by_basic = {}
        for garment, data in weighted_garments.items():
            max_weight = max(max_weight, data['weight'])
            by_basic.setdefault(garment.basic, [])
            by_basic[garment.basic].append({
                'explanations': data['explanations'],
                'garment': garment,
                'weight': data['weight']
            })

        # Normalize the final weights based on the maximum weight value
        if max_weight:
            for basic, garments in by_basic.items():
                for garment in garments:
                    garment['weight'] = garment['weight'] / max_weight

        # Generate faceted recommendations grouped by basic type
        recs = {}
        weight_fetcher = itemgetter('weight')
        for basic, weighted_garments in by_basic.items():
            sorted_garments = sorted(weighted_garments, key=weight_fetcher, reverse=True)

            faceted = {}
            for facet in facets:
                faceted[facet] = facet.apply(sorted_garments)

            recs[basic] = {
                'basic': basic,
                'facets': faceted,
                'garments': sorted_garments
            }

        # TODO: Delete once all steps are implemented
        for query in connection.queries:
            print(query['sql'])
            print(query['time'])
        print('Total queries: %d' % len(connection.queries))

        return recs
