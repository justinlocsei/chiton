from chiton.core.numbers import price_to_integer
from chiton.runway.models import Basic
from chiton.wintour.facets import BaseFacet
from chiton.wintour.pipeline import FacetGroup


# The slugs of all available price groups
GROUP_LOW = 'low'
GROUP_MEDIUM = 'medium'
GROUP_HIGH = 'high'


# The order of the prices groups, by slug
PRICE_GROUP_ORDER = (GROUP_LOW, GROUP_MEDIUM, GROUP_HIGH)


class PriceFacet(BaseFacet):
    """A facet that groups items by price."""

    name = 'Price'
    slug = 'price'

    def provide_profile_data(self, profile):
        basic_prices = {}
        for basic in Basic.objects.all():
            basic_prices[basic.pk] = {
                'low': basic.budget_end,
                'high': basic.luxury_start
            }

        return {
            'basic_prices': basic_prices
        }

    def apply(self, basic, garments, basic_prices=None):
        cutoffs = basic_prices[basic['id']]
        low_cutoff = price_to_integer(cutoffs['low'])
        high_cutoff = price_to_integer(cutoffs['high'])

        groups = {
            GROUP_LOW: [],
            GROUP_MEDIUM: [],
            GROUP_HIGH: []
        }

        # Place items with prices into one of the groups, based on where the
        # item's price falls relative to the basic's cutoff points
        for garment in garments:
            priced_items = [po for po in garment['purchase_options'] if po['price']]
            total_price = sum([pi['price'] for pi in priced_items])
            if not total_price:
                continue

            garment_price = total_price / len(priced_items)
            if garment_price < low_cutoff:
                group_slug = GROUP_LOW
            elif garment_price >= high_cutoff:
                group_slug = GROUP_HIGH
            else:
                group_slug = GROUP_MEDIUM

            groups[group_slug].append(garment['garment']['id'])

        # Create a dict for each group that exposes the IDs of its garments
        facets = []
        for group_slug in PRICE_GROUP_ORDER:
            garment_ids = groups[group_slug]
            facets.append(FacetGroup({
                'garment_ids': garment_ids,
                'slug': group_slug
            }))

        return facets
