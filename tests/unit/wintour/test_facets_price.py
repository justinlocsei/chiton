from decimal import Decimal

import pytest

from chiton.wintour.facets.price import PriceFacet
from chiton.wintour.pipeline import FacetGroup, GarmentRecommendation


@pytest.mark.django_db
class TestPriceFacet:

    def test_groups(self, basic_factory, garment_factory, affiliate_item_factory, pipeline_profile_factory):
        """It creates groups based on the right-weighted price-inflection points of the basic."""
        basic = basic_factory(budget_end=Decimal(15), luxury_start=Decimal(30))

        garment_id_prices = {}
        garments = []
        for price in range(5, 40, 5):
            garment = garment_factory(basic=basic)
            affiliate_item = affiliate_item_factory(garment=garment, price=Decimal(price))
            garment_id_prices[garment.pk] = Decimal(price)

            garments.append(GarmentRecommendation({
                'affiliate_items': [affiliate_item],
                'garment': garment,
                'weight': 1.0
            }, validate=True))

        profile = pipeline_profile_factory()
        with PriceFacet().apply_to_profile(profile) as facet_fn:
            facets = facet_fn(basic, garments)

        facets_by_slug = {}
        for facet in facets:
            facets_by_slug[facet['slug']] = facet

        assert len(facets) == 3
        assert [f['slug'] for f in facets] == ['low', 'medium', 'high']
        assert [FacetGroup(f, validate=True) for f in facets]

        assert facets_by_slug['low']['count'] == 2
        assert facets_by_slug['medium']['count'] == 3
        assert facets_by_slug['high']['count'] == 2

        assert len([id for id in facets_by_slug['low']['garment_ids'] if garment_id_prices[id] < Decimal(15)]) == 2
        assert len([id for id in facets_by_slug['medium']['garment_ids'] if Decimal(15) < garment_id_prices[id] < Decimal(30)]) == 2
        assert len([id for id in facets_by_slug['high']['garment_ids'] if garment_id_prices[id] >= Decimal(30)]) == 2

    def test_groups_price_average(self, basic_factory, garment_factory, affiliate_item_factory, pipeline_profile_factory):
        """It uses the average price of all affiliate items when making groups."""
        basic = basic_factory(budget_end=Decimal(10), luxury_start=Decimal(40))
        garment = garment_factory(basic=basic)
        high_item = affiliate_item_factory(garment=garment, price=Decimal(50))
        low_item = affiliate_item_factory(garment=garment, price=Decimal(5))

        garments = [
            GarmentRecommendation({
                'affiliate_items': [low_item, high_item],
                'garment': garment,
                'weight': 1.0
            }, validate=True)
        ]

        profile = pipeline_profile_factory()
        with PriceFacet().apply_to_profile(profile) as facet_fn:
            facets = facet_fn(basic, garments)

        facets_by_slug = {}
        for facet in facets:
            facets_by_slug[facet['slug']] = facet

        assert len(facets) == 3

        assert facets_by_slug['low']['count'] == 0
        assert facets_by_slug['medium']['count'] == 1
        assert facets_by_slug['high']['count'] == 0

    def test_groups_price_empty(self, basic_factory, garment_factory, affiliate_item_factory, pipeline_profile_factory):
        """It omits garments that lack price information from the facets."""
        basic = basic_factory(budget_end=Decimal(10), luxury_start=Decimal(40))
        garment = garment_factory(basic=basic)
        item = affiliate_item_factory(garment=garment, price=Decimal(0))

        garments = [
            GarmentRecommendation({
                'affiliate_items': [item],
                'garment': garment,
                'weight': 1.0
            }, validate=True)
        ]

        profile = pipeline_profile_factory()
        with PriceFacet().apply_to_profile(profile) as facet_fn:
            facets = facet_fn(basic, garments)

        assert not len([f for f in facets if f['count']])
