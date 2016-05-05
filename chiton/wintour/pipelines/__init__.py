from operator import itemgetter

from django.db import connection

from chiton.closet.models import Garment
from chiton.rack.models import AffiliateItem, AffiliateNetwork


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

        This allows all pipeline steps to pre-process the garments.

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
        instances, whose subkeys provide information on the raw set of garments
        returned, as well as any applied facets.

        Args:
            profile (chiton.wintour.pipeline.PipelineProfile): A wardrobe profile

        Keyword Args:
            debug (bool): Whether to generate debugging statistics

        Returns:
            dict: The garment recommendations
        """
        garments_qs = self.load_garments().select_related('basic')

        filters = self.provide_filters()
        facets = self.provide_facets()
        weights = self.provide_weights()

        # Enable debug mode on all pipeline steps when debugging
        if debug:
            for step in filters + facets + weights:
                step.debug = debug

        # Apply all filters to the set of garments
        for filter_instance in filters:
            with filter_instance.apply_to_profile(profile) as filter_function:
                garments_qs = filter_function(garments_qs)

        # Apply each weight to each garment, and group the results by weight,
        # while keeping data on the weight's value ranges and importance
        weightings = {}
        for weight in weights:
            weighted_garments = []
            max_weight = 0
            min_weight = 0

            with weight.apply_to_profile(profile) as weight_function:
                for garment in garments_qs:
                    applied_weight = weight_function(garment)
                    weighted_garments.append({
                        'garment': garment,
                        'weight': applied_weight
                    })
                    max_weight = max(max_weight, applied_weight)
                    min_weight = min(min_weight, applied_weight)

            # Recalculate the garment weights as a floating-point percentage
            # based on the range of values for the weight
            weight_range = max_weight - min_weight
            if weight_range:
                for weighted_garment in weighted_garments:
                    zeroed_weight = weighted_garment['weight'] - min_weight
                    weighted_garment['weight'] = zeroed_weight / weight_range

            weightings[weight] = {
                'garments': weighted_garments,
                'importance': weight.importance
            }

        # Build a master list of weighted garments by combining the weight
        # values applied to each garment and using each weight's importance to
        # determine the final applied weight
        weighted_garments = {}
        for weight, data in weightings.items():
            for weighted_garment in data['garments']:
                garment = weighted_garment['garment']
                weighted_garments.setdefault(garment, {
                    'explanations': [],
                    'weight': 0
                })
                weighted_garments[garment]['weight'] += weighted_garment['weight'] * data['importance']

                if debug:
                    weighted_garments[garment]['explanations'].append({
                        'name': weight.name,
                        'reasons': weight.get_explanations(garment),
                        'slug': weight.slug
                    })

        # Build a lookup table mapping affiliate-network PKs to network names
        affiliate_networks = {}
        for network in AffiliateNetwork.objects.all():
            affiliate_networks[network.id] = network.name

        # Group garments by their basic type, exposing information on each
        # garment's associated affiliate items
        max_weight = 0
        by_basic = {}
        for affiliate_item in AffiliateItem.objects.all().select_related('garment__basic'):
            garment = affiliate_item.garment
            try:
                data = weighted_garments[garment]
            except KeyError:
                continue

            max_weight = max(max_weight, data['weight'])
            affiliate_link = {
                'name': affiliate_networks[affiliate_item.network_id],
                'url': affiliate_item.url
            }

            by_basic.setdefault(garment.basic, {})
            if garment in by_basic[garment.basic]:
                by_basic[garment.basic][garment]['urls']['vendor'].append(affiliate_link)
            else:
                by_basic[garment.basic][garment] = {
                    'explanations': {
                        'weights': data['explanations']
                    },
                    'garment': garment,
                    'urls': {
                        'vendor': [affiliate_link]
                    },
                    'weight': data['weight']
                }

        # Update all weights to be a floating-point percentage, based on the
        # maximum detected final weight
        if max_weight:
            for basic, garments in by_basic.items():
                for garment, data in garments.items():
                    data['weight'] = data['weight'] / max_weight

        # Generate the final recommendations as a dict keyed by basic type, each
        # of which will have a key for facets as well as a key for all garments,
        # sorted in descending order by weight
        recs = {}
        weight_fetcher = itemgetter('weight')
        for basic, weighted_garments in by_basic.items():
            sorted_garments = sorted(weighted_garments.values(), key=weight_fetcher, reverse=True)

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
