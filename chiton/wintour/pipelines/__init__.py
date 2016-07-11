from itertools import chain
from operator import itemgetter

from chiton.closet.models import Basic, Garment
from chiton.core.queries import cache_query
from chiton.rack.models import AffiliateItem, AffiliateNetwork, ProductImage
from chiton.utils.numbers import price_to_integer
from chiton.wintour.pipeline import BasicRecommendations, BasicOverview, Facet, FacetGroup, GarmentOverview, GarmentRecommendation, PurchaseOption, Recommendations


# Field names for serializing affiliate items
AFFILIATE_ITEM_IMAGE_FIELDS = ('image', 'thumbnail')


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

    def make_recommendations(self, profile, debug=False, max_garments_per_group=None):
        """Make recommendations for a wardrobe profile.

        Args:
            profile (chiton.wintour.profiles.PipelineProfile): A wardrobe profile

        Keyword Args:
            debug (bool): Whether to generate debug statistics
            max_garments_per_group (int): The maximum number of garments to return per facet group

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
        garments_by_basic = self._convert_weighted_garments_to_recommendations(weighted_garments)
        basic_recommendations = self._package_garment_recommendations_as_basic_recommendations(garments_by_basic, facets)
        pruned_recommendations = self._prune_basic_recommendations(basic_recommendations, max_garments_per_group)
        self._current_profile = None

        return Recommendations({
            'basics': pruned_recommendations
        })

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
            with garment_filter.apply_to_profile(self._current_profile) as should_exclude:
                to_keep = [garment for garment in garments if not should_exclude(garment)]
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
        a dict keyed by garment slug.

        Args:
            weightings (dict[chiton.wintour.weights.BaseWeight, list[dict]]): Per-weight garment weightings

        Returns:
            dict[str, dict]: Per-garment weighting information, keyed by slug
        """
        weighted_garments = {}

        for weight, weight_data in weightings.items():
            max_weight = weight_data['max_weight']
            min_weight = weight_data['min_weight']
            weight_range = (max_weight - min_weight) or 1

            for weighted_garment in weight_data['garments']:
                garment = weighted_garment['garment']
                garment_slug = garment.slug
                weighted_garments.setdefault(garment_slug, {
                    'weight': 0
                })

                normalized_weight = (weighted_garment['weight'] - min_weight) / weight_range
                weighted_garments[garment_slug]['weight'] += normalized_weight * weight.importance

                # Add debug information on each logged weight application and
                # on the results of combining the weights
                if weight.debug:
                    weighted_garments[garment_slug].setdefault('explanations', {
                        'normalization': [],
                        'weights': []
                    })
                    explanations = weighted_garments[garment_slug]['explanations']
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

    def _convert_weighted_garments_to_recommendations(self, weighted_garments):
        """Converted weighted garments to per-basic garments recommendations.

        This transforms per-garment weight information into a mapping between
        basic slugs and a further mapping between garment slugs and
        recommendations for the garment.

        Args:
            weighted_garments (dict[str, dict]): Per-garment weighting information keyed by slug

        Returns:
            dict[str, dict]: Per-basic garment recommendations
        """
        by_basic = {}
        max_weight = 0

        # Group garments by their basic type, exposing information on each
        # garment's associated affiliate items
        for affiliate_item in _get_deep_affiliate_items():
            garment_slug = affiliate_item['garment__slug']
            try:
                garment_data = weighted_garments[garment_slug]
            except KeyError:
                continue

            basic_slug = affiliate_item['garment__basic__slug']
            max_weight = max(max_weight, garment_data['weight'])

            # Serialize affiliate items as purchase options
            purchase_option = PurchaseOption({
                'id': affiliate_item['id'],
                'price': price_to_integer(affiliate_item['price']),
                'network_name': affiliate_item['network__name'],
                'url': affiliate_item['url']
            })

            # Add serialized image information to each purchase option
            for image_field in AFFILIATE_ITEM_IMAGE_FIELDS:
                purchase_option[image_field] = affiliate_item.get('%s__file' % image_field, None)

            # Add each garment recommendation to its basic
            by_basic.setdefault(basic_slug, {})
            try:
                by_basic[basic_slug][garment_slug]['purchase_options'].append(purchase_option)
            except KeyError:
                by_basic[basic_slug][garment_slug] = GarmentRecommendation({
                    'garment': GarmentOverview({
                        'brand': affiliate_item['garment__brand__name'],
                        'id': affiliate_item['garment_id'],
                        'name': affiliate_item['garment__name']
                    }),
                    'purchase_options': [purchase_option],
                    'weight': garment_data['weight']
                })

                explanations = garment_data.get('explanations', None)
                if explanations:
                    by_basic[basic_slug][garment_slug]['explanations'] = explanations

        # Update all weights to use floating-point percentages calibrated
        # against the maximum total weight, and sort affiliate items by price
        if max_weight:
            for basic, garments in by_basic.items():
                for garment, data in garments.items():
                    data['weight'] = data['weight'] / max_weight

        return by_basic

    def _package_garment_recommendations_as_basic_recommendations(self, garments_by_basic, facets):
        """Converted per-basic garments recommendations to basic recommendations.

        This transforms a mapping of basics to garments into a series of basic
        recommendations that expose the garments, ordered by weight.

        Args:
            garments_by_basic (dict[str, dict]): Per-basic garment recommendations
            facets (list[chiton.wintour.facets.BaseFacet]): The facets to apply to each basic's recommendations

        Returns:
            list[chiton.wintour.pipeline.BasicRecommendations]: Per-basic garment recommendations
        """
        recommendations = []
        basic_data = _build_basic_lookup_table()

        # Convert the basic and garment mappings into a list of basic
        # recommendations, sorted alphabetically, with garment recommendations
        # sorted by weight
        weight_fetcher = itemgetter('weight')
        for basic_slug in sorted(garments_by_basic.keys()):
            recommendations.append(BasicRecommendations({
                'basic': BasicOverview(basic_data[basic_slug]),
                'facets': [],
                'garments': sorted(garments_by_basic[basic_slug].values(), key=weight_fetcher, reverse=True)
            }))

        # Add facets to each basic's recommendations
        for facet in facets:
            with facet.apply_to_profile(self._current_profile) as apply_facet:
                for basic in recommendations:
                    groups = apply_facet(basic['basic'], basic['garments'])
                    basic['facets'].append(Facet({
                        'name': facet.name,
                        'groups': [FacetGroup(group) for group in groups],
                        'slug': facet.slug
                    }))

        return recommendations

    def _prune_basic_recommendations(self, basic_recommendations, max_garments_per_group):
        """Remove garments that exceed the maximum number per facet group.

        This ensure that each facet group has at most the given number of
        garments, then removes all garment entries that are not in those groups.

        Args:
            basic_recommendations (list[chiton.wintour.pipeline.BasicRecommendations]): Basic recommendations
            max_garments_per_group (int): The maximum number of garments per facet group

        Returns:
            list[chiton.wintour.pipeline.BasicRecommendations]: The pruned basic recommendations
        """
        if max_garments_per_group is None:
            return basic_recommendations

        for basic_recommendation in basic_recommendations:
            include_ids = []

            for facet in basic_recommendation['facets']:
                for i, group in enumerate(facet['groups']):
                    subset_ids = group['garment_ids'][0:max_garments_per_group]
                    facet['groups'][i]['garment_ids'] = subset_ids
                    include_ids += subset_ids

            include_ids = set(include_ids)
            basic_recommendation['garments'] = [
                garment for garment in basic_recommendation['garments']
                if garment['garment']['id'] in include_ids
            ]

        return basic_recommendations


@cache_query(AffiliateItem, AffiliateNetwork, Garment, ProductImage)
def _get_deep_affiliate_items():
    """Get all affiliate items, with extended relations selected.

    Returns:
        django.db.models.query.QuerySet: A queryset of all affiliate items
    """
    return (
        AffiliateItem.objects.all()
        .select_related('garment', 'garment__basic', 'garment__brand', 'image', 'network', 'thumbnail')
        .order_by('-price')
        .values(
            'garment_id', 'garment__name', 'garment__slug',
            'garment__basic__slug', 'garment__brand__name',
            'id', 'price', 'url',
            'network__name',
            'image__height', 'image__width', 'image__file',
            'thumbnail__height', 'thumbnail__width', 'thumbnail__file'
        )
    )


@cache_query(Basic)
def _build_basic_lookup_table():
    """Create a lookup table that maps basic slugs to basic data.

    Returns:
        dict[str, dict]: A lookup for basic data
    """
    lookup = {}

    for basic in Basic.objects.all().values('id', 'name', 'slug'):
        lookup[basic['slug']] = basic

    return lookup
