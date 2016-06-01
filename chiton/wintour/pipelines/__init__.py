from itertools import chain
from operator import itemgetter

from chiton.closet.models import Garment
from chiton.rack.models import AffiliateItem
from chiton.wintour.pipeline import BasicRecommendations, GarmentRecommendation


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

        for step in self._get_all_steps():
            garments = step.prepare_garments(garments)

        return garments

    def provide_facets(self):
        """Provide all facets for the pipeline.

        Returns:
            list: A list of all facet classes
        """
        return []

    def provide_garment_filters(self):
        """Provide all garment filters for the pipeline.

        Returns:
            list: A list of all garment-filter classes
        """
        return []

    def provide_query_filters(self):
        """Provide all query filters for the pipeline.

        Returns:
            list: A list of all query-filter classes
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
        garments_qs = self._filter_garments_queryset(query_filters, garments_qs)
        garments = self._filter_garments(garment_filters, garments_qs)
        weightings = self._weight_garments(weights, garments)
        weighted_garments = self._combine_garment_weights(weightings)
        garments_by_basic = self._normalize_weightings(weighted_garments)
        recommendations = self._facet_garments(facets, garments_by_basic)
        self._current_profile = None

        return recommendations

    def _get_all_steps(self):
        """Get a list of all steps for the pipeline.

        Returns:
            list: All step instances
        """
        steps = [
            self.provide_facets(),
            self.provide_garment_filters(),
            self.provide_query_filters(),
            self.provide_weights()
        ]
        return list(chain.from_iterable(steps))

    def _filter_garments_queryset(self, query_filters, garments_qs):
        """Apply a series of filters to a queryset of garments.

        This applies each filter's logic to the queryset, and returns the
        unevaluated queryset primed with filtering calls.

        Args:
            query_filters (list): A list of BaseQueryFilter subclass instances
            garments_qs (django.db.models.query.QuerySet): A queryset of garments

        Returns:
            django.db.models.query.QuerySet: The filtered garment queryset
        """
        for query_filter in query_filters:
            with query_filter.apply_to_profile(self._current_profile) as filter_garments:
                garments_qs = filter_garments(garments_qs)

        return garments_qs

    def _filter_garments(self, garment_filters, garments):
        """Apply a series of filters to a individual garments.

        This applies each filter's logic to the each garment in the input, and
        returns a list of all non-excluded garments.

        Args:
            garment_filters (list): A list of BaseGarmentFilter subclass instances
            garments (django.db.models.query.QuerySet): A queryset of garments

        Returns:
            list: The evaluated queryset, with any excluded garments removed
        """
        for garment_filter in garment_filters:
            to_keep = []
            with garment_filter.apply_to_profile(self._current_profile) as should_exclude:
                for garment in garments:
                    if not should_exclude(garment):
                        to_keep.append(garment)
            garments = to_keep

        return garments

    def _weight_garments(self, weights, garments):
        """Apply a series of weights to a list of garments for a profile.

        This applies each weight to each garment, and exposes the results in a
        dict keyed by the weight instance with values of the weighted garments
        and the weight's relative importance.

        This returns a dict that maps weight instances to weighted garments,
        with the garments sorted in descending order by weight and rendered as
        dicts that expose the garment instance and an applied weight.

        Args:
            weights (list): A list of BaseWeight subclass instances
            garments (list): An unordered list of garments

        Returns:
            dict: A mapping between weight instances and weighted garments
        """
        weightings = {}

        for weight in weights:
            weighted_garments = []
            max_weight = 0
            min_weight = 0

            # Apply the weight to the garment, and update the max and min
            # weights in response to the results
            with weight.apply_to_profile(self._current_profile) as weight_function:
                for garment in garments:
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

            weightings[weight] = weighted_garments

        return weightings

    def _combine_garment_weights(self, weightings):
        """Combine all weights applied to a garment.

        This expects to receive a dict keyed by weight instances with values of
        the garments in the weight and the weight's importance.  This structure
        is used to build a dict keyed by garment instance that exposes core
        garment data and weighting metadata.

        Args:
            weightings (dict): A mapping between weight instances and weighted garments

        Returns:
            dict: A dict keyed by garment instance that provides weight and debug data
        """
        weighted_garments = {}

        for weight, garments in weightings.items():
            for weighted_garment in garments:
                garment = weighted_garment['garment']
                weighted_garments.setdefault(garment, {
                    'explanations': {
                        'normalization': [],
                        'weights': []
                    },
                    'weight': 0
                })
                normalized_weight = weighted_garment['weight'] * weight.importance
                weighted_garments[garment]['weight'] += normalized_weight

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
                        'weight': weighted_garment['weight']
                    })

        return weighted_garments

    def _normalize_weightings(self, weighted_garments):
        """Normalize weighted garments.

        This expects a dict keyed by a garment instance with values that
        describe the garment's weighting.  This information is converted into a
        dict keyed by a basic instance that exposes normalized weighting data
        and supplemental garment data.

        Args:
            dict: A mapping between garment instances and weight/debug information

        Returns:
            dict: A mapping between basic instances and garment recommendations
        """
        by_basic = {}
        max_weight = 0

        # Group garments by their basic type, exposing information on each
        # garment's associated affiliate items
        for affiliate_item in AffiliateItem.objects.all().select_related('garment__basic', 'image', 'thumbnail', 'network__name'):
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
        # against the maximum total weight
        if max_weight:
            for basic, garments in by_basic.items():
                for garment, data in garments.items():
                    data['weight'] = data['weight'] / max_weight

        return by_basic

    def _facet_garments(self, facets, garments_by_basic):
        """Create faceted garment groups.

        Args:
            facets (list): A list of BaseFacet subclass instances
            garments_by_basic (dict): A mapping of basic instances to annotated garment instances

        Returns:
            dict: A mapping between basic instances and recommendations
        """
        faceted = {}

        # Generate the mapping between basics and garments, with a placeholder
        # for the faceted data
        weight_fetcher = itemgetter('weight')
        for basic, weighted_garments in garments_by_basic.items():
            faceted[basic] = BasicRecommendations({
                'facets': {},
                'garments': sorted(weighted_garments.values(), key=weight_fetcher, reverse=True)
            })

        # Apply all facets to the data
        for facet in facets:
            with facet.apply_to_profile(self._current_profile) as apply_facet:
                for basic, data in faceted.items():
                    faceted[basic]['facets'][facet] = apply_facet(basic, data['garments'])

        return faceted
