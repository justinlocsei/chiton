from decimal import Decimal

import pytest

from chiton.wintour.facets import BaseFacet
from chiton.wintour.garment_filters import BaseGarmentFilter
from chiton.wintour.pipeline import FacetGroup
from chiton.wintour.pipelines import BasePipeline
from chiton.wintour.query_filters import BaseQueryFilter
from chiton.wintour.weights import BaseWeight


class TestQueryFilter(BaseQueryFilter):
    name = 'Test Query Filter'
    slug = 'test-query-filter'


class TestGarmentFilter(BaseGarmentFilter):
    name = 'Test Garment Filter'
    slug = 'test-garment-filter'


class TestWeight(BaseWeight):
    name = 'Test Weight'
    slug = 'test-weight'


class TestFacet(BaseFacet):
    name = 'Test Facet'
    slug = 'test-face'


@pytest.fixture
def pipeline_factory():
    def create_pipeline(query_filters=[], garment_filters=[], weights=[], facets=[]):
        class Pipeline(BasePipeline):

            def provide_query_filters(self):
                return query_filters

            def provide_garment_filters(self):
                return garment_filters

            def provide_weights(self):
                return weights or [TestWeight()]

            def provide_facets(self):
                return facets

        return Pipeline()

    return create_pipeline


@pytest.mark.django_db
class TestBasePipeline:

    def test_provide_garments(self, garment_factory):
        """It provides the full queryset of garments."""
        garment_factory()
        garment_factory()

        garments = BasePipeline().provide_garments()

        assert garments.count() == 2

    def test_load_garments(self, garment_factory, pipeline_factory):
        """It allows each pipeline step to modify the garment queryset."""
        def slice_garments(garments):
            return garments[:garments.count() - 1]

        class QueryFilter(TestQueryFilter):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        class GarmentFilter(TestGarmentFilter):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        class Weight(TestWeight):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        class Facet(TestFacet):
            def prepare_garments(self, garments):
                return slice_garments(garments)

        pipeline = pipeline_factory(
            query_filters=[QueryFilter()],
            garment_filters=[GarmentFilter()],
            weights=[Weight()],
            facets=[Facet()]
        )

        for i in range(0, 5):
            garment_factory()

        garments = pipeline.load_garments()
        assert garments.count() == 1

    def test_make_recommendations(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It produces per-basic garment recommendations for a wardrobe profile."""
        class QueryFilter(TestQueryFilter):
            def apply(self, garments):
                return garments.exclude(name='3')

        class GarmentFilter(TestGarmentFilter):
            def apply(self, garment):
                return garment.name == '2'

        class Weight(TestWeight):
            def apply(self, garment):
                return int(garment.name)

        class Facet(TestFacet):
            slug = 'test'

            def apply(self, basic, garments):
                return [FacetGroup({
                    'count': len(garments),
                    'garment_ids': [g['garment'].pk for g in garments],
                    'slug': 'all'
                })]

        skirts = basic_factory()
        shirts = basic_factory()

        skirt_one = garment_factory(basic=skirts, name='1')
        skirt_two = garment_factory(basic=skirts, name='2')
        skirt_three = garment_factory(basic=skirts, name='3')
        shirt_one = garment_factory(basic=shirts, name='1')
        shirt_four = garment_factory(basic=shirts, name='4')

        affiliate_item_factory(garment=skirt_one)
        affiliate_item_factory(garment=skirt_two)
        affiliate_item_factory(garment=skirt_three)
        affiliate_item_factory(garment=shirt_one)
        affiliate_item_factory(garment=shirt_four)

        facet = Facet()
        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(
            query_filters=[QueryFilter()],
            garment_filters=[GarmentFilter()],
            weights=[Weight()],
            facets=[facet]
        )

        recommendations = pipeline.make_recommendations(profile)
        assert len(recommendations.keys()) == 2

        skirt_recs = recommendations[skirts]
        shirt_recs = recommendations[shirts]

        assert [g['weight'] for g in skirt_recs['garments']] == [0.25]
        assert [g['garment'] for g in skirt_recs['garments']] == [skirt_one]

        assert [g['weight'] for g in shirt_recs['garments']] == [1.0, 0.25]
        assert [g['garment'] for g in shirt_recs['garments']] == [shirt_four, shirt_one]

        skirt_facets = skirt_recs['facets'][facet]
        shirt_facets = shirt_recs['facets'][facet]

        assert len(skirt_facets) == 1
        assert skirt_facets[0]['garment_ids'] == [skirt_one.pk]

        assert len(shirt_facets) == 1
        assert set(shirt_facets[0]['garment_ids']) == set([shirt_four.pk, shirt_one.pk])

    def test_make_recommendations_affiliate_items(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It exposes information on each garment's available affiliate items, sorted by price."""
        class Weight(TestWeight):
            def apply(self, garment):
                return int(garment.name)

        basic = basic_factory()
        garment_single = garment_factory(basic=basic, name='1')
        garment_multi = garment_factory(basic=basic, name='2')

        item_one_one = affiliate_item_factory(garment=garment_single)
        item_two_one = affiliate_item_factory(garment=garment_multi, price=Decimal(10))
        item_two_two = affiliate_item_factory(garment=garment_multi, price=Decimal(20))

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[Weight()])

        recommendations = pipeline.make_recommendations(profile)
        garments = recommendations[basic]['garments']

        assert len(garments) == 2
        assert [g['garment'] for g in garments] == [garment_multi, garment_single]

        garment_multi_items = garments[0]['affiliate_items']
        assert len(garment_multi_items) == 2
        assert garment_multi_items == [item_two_two, item_two_one]

        garment_single_items = garments[1]['affiliate_items']
        assert len(garment_single_items) == 1
        assert garment_single_items == [item_one_one]

    def test_make_recommendations_queryset_filters(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It combines all queryset filters."""
        class TallFilter(TestQueryFilter):
            def apply(self, garments):
                return garments.filter(is_tall_sized=False)

        class PetiteFilter(TestQueryFilter):
            def apply(self, garments):
                return garments.filter(is_petite_sized=False)

        basic = basic_factory()
        affiliate_item_factory(garment=garment_factory(basic=basic, is_regular_sized=True))
        affiliate_item_factory(garment=garment_factory(basic=basic, is_petite_sized=True))
        affiliate_item_factory(garment=garment_factory(basic=basic, is_tall_sized=True))

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(query_filters=[TallFilter(), PetiteFilter()])

        recommendations = pipeline.make_recommendations(profile)

        assert len(recommendations[basic]['garments']) == 1

    def test_make_recommendations_garment_filters(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It combines all garment filters."""
        class PantsFilter(TestGarmentFilter):
            def apply(self, garment):
                return garment.name == 'Pants'

        class ShirtFilter(TestGarmentFilter):
            def apply(self, garment):
                return garment.name == 'Shirt'

        basic = basic_factory()
        affiliate_item_factory(garment=garment_factory(basic=basic, name='Dress'))
        affiliate_item_factory(garment=garment_factory(basic=basic, name='Pants'))
        affiliate_item_factory(garment=garment_factory(basic=basic, name='Shirt'))

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(garment_filters=[PantsFilter(), ShirtFilter()])

        recommendations = pipeline.make_recommendations(profile)

        assert len(recommendations[basic]['garments']) == 1

    def test_make_recommendations_weights_normalization(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It normalizes a single weight's range of values as floating-point percentage sorted in descending order."""
        class Weight(TestWeight):
            def apply(self, garment):
                return int(garment.name)

        basic = basic_factory()
        positive_garment = garment_factory(basic=basic, name='100')
        negative_garment = garment_factory(basic=basic, name='-100')
        zero_garment = garment_factory(basic=basic, name='0')

        affiliate_item_factory(garment=positive_garment)
        affiliate_item_factory(garment=negative_garment)
        affiliate_item_factory(garment=zero_garment)

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[Weight()])

        recommendations = pipeline.make_recommendations(profile)

        garments = recommendations[basic]['garments']
        assert len(garments) == 3

        weights_by_garment = {}
        for garment in garments:
            weights_by_garment[garment['garment']] = garment['weight']

        assert weights_by_garment[positive_garment] == 1.0
        assert weights_by_garment[negative_garment] == 0.0
        assert weights_by_garment[zero_garment] == 0.5

        assert [g['weight'] for g in garments] == [1.0, 0.5, 0.0]

    def test_make_recommendations_weights_coalesce(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It combines multiple weights for a garment into per-garment normalized weights."""
        class ConstantWeight(TestWeight):
            def apply(self, garment):
                return int(garment.name)

        class AbsoluteWeight(TestWeight):
            def apply(self, garment):
                return abs(int(garment.name))

        basic = basic_factory()
        positive_garment = garment_factory(basic=basic, name='1')
        negative_garment = garment_factory(basic=basic, name='-1')

        affiliate_item_factory(garment=positive_garment)
        affiliate_item_factory(garment=negative_garment)

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(weights=[AbsoluteWeight(importance=3), ConstantWeight()])

        recommendations = pipeline.make_recommendations(profile)

        weights_by_garment = {}
        for garment in recommendations[basic]['garments']:
            weights_by_garment[garment['garment']] = garment['weight']

        assert weights_by_garment[positive_garment] == 1.0
        assert weights_by_garment[negative_garment] == 0.75

    def test_make_recommendations_weights_debug(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It adds debugging information for weights when requested."""
        class Weight(TestWeight):
            name = 'Custom Weight'

            def apply(self, garment):
                if self.debug:
                    self.explain_weight(garment, 2.0, "Constant weight")
                return 2.0

        basic = basic_factory()
        affiliate_item_factory(garment=garment_factory(basic=basic))

        query_filter = TestQueryFilter()
        garment_filter = TestGarmentFilter()
        facet = TestFacet()
        weight = Weight()

        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(
            query_filters=[query_filter],
            garment_filters=[garment_filter],
            weights=[weight],
            facets=[facet]
        )

        recommendations = pipeline.make_recommendations(profile, debug=True)
        garments = recommendations[basic]['garments']

        assert len(garments) == 1

        explanations = garments[0]['explanations']
        normalization = explanations['normalization']
        weights = explanations['weights']

        assert len(normalization) == 1
        assert len(weights) == 1

        normalized = normalization[0]
        assert normalized['importance'] == 1
        assert normalized['weight'] == 1.0
        assert normalized['name'] == 'Custom Weight'

        weighted = weights[0]
        assert weighted['name'] == 'Custom Weight'
        assert len(weighted['reasons']) == 1

        reason = weighted['reasons'][0]
        assert reason['reason'] == 'Constant weight'
        assert reason['weight'] == 2.0

    def test_make_recommendations_facets(self, basic_factory, affiliate_item_factory, garment_factory, pipeline_factory, pipeline_profile_factory):
        """It creates facets for the final recommendations."""
        class NameFacet(TestWeight):
            slug = 'name'

            def apply(self, basic, garments):
                gs = [g['garment'] for g in garments]
                return [
                    FacetGroup({
                        'count': 1,
                        'garment_ids': [g.pk for g in gs if g.name == 'Shirt'],
                        'slug': 'low'
                    }),
                    FacetGroup({
                        'count': 1,
                        'garment_ids': [g.pk for g in gs if g.name == 'Jeans'],
                        'slug': 'high'
                    })
                ]

        basic = basic_factory()
        shirt = garment_factory(basic=basic, name='Shirt')
        jeans = garment_factory(basic=basic, name='Jeans')

        affiliate_item_factory(garment=shirt)
        affiliate_item_factory(garment=jeans)

        name_facet = NameFacet()
        profile = pipeline_profile_factory()
        pipeline = pipeline_factory(facets=[name_facet])

        recommendations = pipeline.make_recommendations(profile)
        facets = recommendations[basic]['facets']

        assert name_facet in facets
        name_facets = facets[name_facet]

        assert len(name_facets) == 2
        assert name_facets[0]['slug'] == 'low'
        assert name_facets[1]['slug'] == 'high'

        assert name_facets[0]['garment_ids'] == [shirt.pk]
        assert name_facets[1]['garment_ids'] == [jeans.pk]

    def test_make_recommendations_empty(self, garment_factory, pipeline_profile_factory):
        """It returns empty recommendations for a default pipeline."""
        garment_factory()

        profile = pipeline_profile_factory()
        pipeline = BasePipeline()

        assert pipeline.make_recommendations(profile) == {}
