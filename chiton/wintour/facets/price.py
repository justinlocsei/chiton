from chiton.runway.models import Basic
from chiton.wintour.facets import BaseFacet


# The order of the prices groups, by slug
PRICE_GROUP_ORDER = ('budget', 'normal', 'luxury')


class PriceFacet(BaseFacet):
    """A facet that groups items by price."""

    name = 'Price'
    slug = 'price'

    def provide_profile_data(self, profile):
        basic_prices = {}
        for basic in Basic.objects.all():
            basic_prices[basic.pk] = {
                'budget': basic.budget_end,
                'luxury': basic.luxury_start
            }

        return {
            'basic_prices': basic_prices
        }

    def apply(self, basic, garments, basic_prices=None):
        cutoffs = basic_prices[basic.pk]

        groups = {
            'budget': [],
            'normal': [],
            'luxury': []
        }

        # Place items with prices into one of the groups, based on where the
        # item's price falls relative to the basic's cutoff points
        for garment in garments:
            priced_items = [ai for ai in garment['affiliate_items'] if ai.price]
            total_price = sum([pi.price for pi in priced_items])
            if not total_price:
                continue

            garment_price = total_price / len(priced_items)
            if garment_price <= cutoffs['budget']:
                group_name = 'budget'
            elif garment_price >= cutoffs['luxury']:
                group_name = 'luxury'
            else:
                group_name = 'normal'

            groups[group_name].append(garment['garment'].pk)

        # Create a dict for each group that exposes the IDs of its garments
        facets = []
        for group_slug in PRICE_GROUP_ORDER:
            garment_ids = groups[group_slug]
            facets.append({
                'count': len(garment_ids),
                'garment_ids': garment_ids,
                'slug': group_slug
            })

        return facets
