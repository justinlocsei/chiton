from itertools import chain
from operator import itemgetter

from chiton.closet.models import Garment
from chiton.rack.models import AffiliateItem
from chiton.wintour.pipeline import BasicRecommendations, GarmentRecommendation


class BasePipeline:
    """The base class for all pipelines."""

    def provide_garments(self):
        """Provide the set of all garments to pass through the pipeline.

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

        for step in self._get_all_steps():
            garments = step.prepare_garments(garments)

        return garments

    def provide_facets(self):
        """Provide the facets used by the pipeline.

        Returns:
            list[chiton.wintour.facets.BaseFacet]: Instances of the facet classes to use
        """
        return []

    def provide_garment_filters(self):
        """Provide the garment filters used by the pipeline.

        Returns:
            list[chiton.wintour.facets.BaseGarmentFilter]: Instances of the garment-filter classes to use
        """
        return []

    def provide_query_filters(self):
        """Provide the query filters used by the pipeline.

        Returns:
            list[chiton.wintour.facets.BaseQueryFilter]: Instances of the query-filter classes to use
        """
        return []

    def provide_weights(self):
        """Provide the weights used by the pipeline.

        Returns:
            list[chiton.wintour.facets.BaseWeight]: Instances of the weight classes to use
        """
        return []

    def make_recommendations(self, profile, debug=False):
        """Make recommendations for a wardrobe profile.

        Args:
            profile (chiton.wintour.pipeline.PipelineProfile): A wardrobe profile

        Keyword Args:
            debug (bool): Whether to generate debug statistics

        Returns:
            dict[chiton.runway.models.Basic, chiton.wintour.pipeline.BasicRecommendations]: The per-basic garment recommendations
        """
        garments_qs = self.load_garments().select_related('basic')

        facets = self.provide_facets()
        garment_filters = self.provide_garment_filters()
        query_filters = self.provide_query_filters()
        weights = self.provide_weights()

        # Enable debug mode on all pipeline steps when debugging
        if debug:
            for step in facets + garment_filters + query_filters + weights:
                step.debug = debug

        # Generate the master list of weighted garments as a dict keyed by a
        # basic instance with garment core data and metadata
        self._current_profile = profile
        garments_qs = self._filter_garments_queryset(garments_qs, query_filters)
        garments = self._filter_garments(garments_qs, garment_filters)
        weightings = self._weight_garments(garments, weights)
        weighted_garments = self._coalesce_garment_weights(weightings)
        garments_by_basic = self._convert_garment_weights_to_basic_weights(weighted_garments)
        recommendations = self._finalize_recommendations(garments_by_basic, facets)
        self._current_profile = None

        return recommendations

    def _get_all_steps(self):
        """Get a list of all steps for the pipeline.

        Returns:
            list[chiton.wintour.pipeline.PipelineStep]: All step instances
        """
        steps = [
            self.provide_facets(),
            self.provide_garment_filters(),
            self.provide_query_filters(),
            self.provide_weights()
        ]
        return list(chain.from_iterable(steps))

    def _filter_garments_queryset(self, garments, query_filters):
        """Apply a series of filters to a queryset of garments.

        This applies each filter's logic to the queryset, and returns the
        unevaluated queryset primed with filtering calls.

        Args:
            garments (django.db.models.query.QuerySet): A queryset of garments
            query_filters (list[chiton.wintour.query_filters.BaseQueryFilter]): Instances of query filters

        Returns:
            django.db.models.query.QuerySet: The filtered garment queryset
        """
        for query_filter in query_filters:
            with query_filter.apply_to_profile(self._current_profile) as filter_garments:
                garments = filter_garments(garments)

        return garments

    def _filter_garments(self, garments, garment_filters):
        """Apply a series of filters to a individual garments.

        This applies each filter's logic to the each garment in the input, and
        returns a list of all non-excluded garments.

        Args:
            garments (django.db.models.query.QuerySet): A queryset of garments
            garment_filters (list[chiton.wintour.garment_filters.BaseGarmentFilter]): Instances of garment filters

        Returns:
            list[chiton.closet.models.Garment]: The evaluated queryset, with any excluded garments removed
        """
        for garment_filter in garment_filters:
            to_keep = []
            with garment_filter.apply_to_profile(self._current_profile) as should_exclude:
                for garment in garments:
                    if not should_exclude(garment):
                        to_keep.append(garment)
            garments = to_keep

        return garments

    def _weight_garments(self, garments, weights):
        """Apply a series of weights to a list of garments for a profile.

        This applies each weight to every garment in the list and exposes this
        information in a dict keyed by weight.

        Args:
            garments (list[chiton.closet.models.Garment]): Garments without ordering
            weights (list[chiton.wintour.weights.BaseWeight]): Instances of weights

        Returns:
            dict[chiton.wintour.weights.BaseWeight, list[dict]]: Per-weight weightings for every garment
        """
        weightings = {}

        for weight in weights:

            # Apply the weight to the garment, and update the max and min
            # weights in response to the results
            with weight.apply_to_profile(self._current_profile) as weight_function:
                weighted_garments = [
                    {'garment': garment, 'weight': weight_function(garment)}
                    for garment in garments
                ]

            # Expose the garments and the max and min weight value for the
            # current weight to support later normalization
            weight_values = [0] + [g['weight'] for g in weighted_garments]
            weightings[weight] = {
                'garments': weighted_garments,
                'max_weight': max(weight_values),
                'min_weight': min(weight_values)
            }

        return weightings

    def _coalesce_garment_weights(self, weightings):
        """Transform per-weight garment weightings into per-garment weightings.

        This takes the per-weight values for each garment and combines them in
        a dict keyed by garment.

        Args:
            weightings (dict[chiton.wintour.weights.BaseWeight, list[dict]]): Per-weight garment weightings

        Returns:
            dict[chiton.closet.models.Garment, dict]: Per-garment weighting information
        """
        weighted_garments = {}

        for weight, weight_data in weightings.items():
            max_weight = weight_data['max_weight']
            min_weight = weight_data['min_weight']
            weight_range = (max_weight - min_weight) or 1

            for weighted_garment in weight_data['garments']:
                garment = weighted_garment['garment']
                weighted_garments.setdefault(garment, {
                    'explanations': {
                        'normalization': [],
                        'weights': []
                    },
                    'weight': 0
                })

                normalized_weight = (weighted_garment['weight'] - min_weight) / weight_range
                weighted_garments[garment]['weight'] += normalized_weight * weight.importance

                # Add debug information on each logged weight application and
                # on the results of combining the weights
                if weight.debug:
                    explanations = weighted_garments[garment]['explanations']
                    explanations['weights'].append({
                        'name': weight.name,
                        'reasons': weight.get_explanations(garment)
                    })
                    explanations['normalization'].append({
                        'importance': weight.importance,
                        'name': weight.name,
                        'weight': normalized_weight
                    })

        return weighted_garments

    def _convert_garment_weights_to_basic_weights(self, weighted_garments):
        """Normalize weighted garments.

        This transforms per-garment weight information into a dict keyed by
        basics that exposes weight values that are normalized to the global max,
        with each basic's garments sorted by weight.

        Args:
            dict[chiton.closet.models.Garment, dict]: Per-garment weighting information

        Returns:
            dict[chiton.runway.models.Basic, dict[chiton.closet.models.Garment, chiton.wintour.pipeline.GarmentRecommendation]]: Per-basic garment recommendations
        """
        by_basic = {}
        max_weight = 0

        # Get all affiliate items with pre-selected fields and order them by
        # price, to ensure that each garment's items are ordered by price
        affiliate_items = (
            AffiliateItem.objects.all()
            .select_related('garment__basic', 'image', 'thumbnail', 'network__name')
            .order_by('-price')
        )

        # Group garments by their basic type, exposing information on each
        # garment's associated affiliate items
        for affiliate_item in affiliate_items:
            garment = affiliate_item.garment
            try:
                garment_data = weighted_garments[garment]
            except KeyError:
                continue

            max_weight = max(max_weight, garment_data['weight'])

            by_basic.setdefault(garment.basic, {})
            if garment in by_basic[garment.basic]:
                by_basic[garment.basic][garment]['affiliate_items'].append(affiliate_item)
            else:
                by_basic[garment.basic][garment] = GarmentRecommendation({
                    'affiliate_items': [affiliate_item],
                    'explanations': garment_data['explanations'],
                    'garment': garment,
                    'weight': garment_data['weight']
                })

        # Update all weights to use floating-point percentages calibrated
        # against the maximum total weight, and sort affiliate items by price
        if max_weight:
            for basic, garments in by_basic.items():
                for garment, data in garments.items():
                    data['weight'] = data['weight'] / max_weight

        return by_basic

    def _finalize_recommendations(self, garments_by_basic, facets):
        """Convert raw per-basic recommendations into annotated recommendations.

        Args:
            dict[chiton.runway.models.Basic, dict[chiton.closet.models.Garment, chiton.wintour.pipeline.GarmentRecommendation]]: Per-basic garment recommendations
            facets (list[chiton.wintour.facets.BaseFacet]): Instances of facet classes

        Returns:
            dict[chiton.runway.models.Basic, chiton.wintour.pipeline.BasicRecommendations]: Per-basic annotated garment recommendations
        """
        basic_recommendations = {}

        # Build the initial recommendations by sorting each basic's garments by
        # weight and adding a placeholder for facets
        weight_fetcher = itemgetter('weight')
        for basic, garments in garments_by_basic.items():
            basic_recommendations[basic] = BasicRecommendations({
                'facets': {},
                'garments': sorted(garments.values(), key=weight_fetcher, reverse=True)
            })

        # Apply all facets to each basic's garments
        for facet in facets:
            with facet.apply_to_profile(self._current_profile) as apply_facet:
                for basic, data in basic_recommendations.items():
                    basic_recommendations[basic]['facets'][facet] = apply_facet(basic, data['garments'])

        return basic_recommendations
