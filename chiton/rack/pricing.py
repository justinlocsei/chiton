from chiton.rack.models import AffiliateItem


def update_basic_price_points(basic):
    """Update the price points for a basic using the price of its offerings.

    This sets the budget and luxury points by examining the top and bottom
    quarter of all items.

    Args:
        basic (chiton.runway.models.Basic): A basic

    Returns:
        tuple: A two-tuple defining the budget start point and the luxury end point
    """
    prices = (AffiliateItem.objects
        .filter(garment__basic=basic)
        .order_by('price')
        .values_list('price', flat=True))
    price_count = len(prices)

    if not price_count:
        return (None, None)

    quarter_index = max(int(price_count / 4) - 1, 0)
    budget_end = prices[max(quarter_index, 0)]
    luxury_start = prices[max(price_count - 1 - quarter_index, 0)]

    basic.budget_end = budget_end
    basic.luxury_start = luxury_start
    basic.save()

    return (budget_end, luxury_start)
