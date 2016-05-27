from decimal import Decimal

import pytest

from chiton.rack.pricing import update_basic_price_points


@pytest.mark.django_db
class TestUpdateBasicPricePoints:

    def test_price_point_distribution(self, basic_factory, garment_factory, affiliate_item_factory):
        """It sets the new budget and luxury points on the lower and upper quarter of garments."""
        basic = basic_factory()
        garment = garment_factory(basic=basic)
        affiliate_item_factory(garment=garment, price=Decimal(10))
        affiliate_item_factory(garment=garment, price=Decimal(90))
        affiliate_item_factory(garment=garment, price=Decimal(100))
        affiliate_item_factory(garment=garment, price=Decimal(1000))

        assert not basic.budget_end
        assert not basic.luxury_start

        update_basic_price_points(basic)

        assert basic.budget_end == Decimal(10)
        assert basic.luxury_start == Decimal(1000)

    def test_price_return(self, basic_factory, garment_factory, affiliate_item_factory):
        """It returns the new price points as a two-tuple of the budget and luxury price."""
        basic = basic_factory()
        garment = garment_factory(basic=basic)
        affiliate_item_factory(garment=garment, price=Decimal(100))

        budget_end, luxury_start = update_basic_price_points(basic)

        assert budget_end == Decimal(100)
        assert luxury_start == Decimal(100)

    def test_empty(self, basic_factory):
        """It does not modify the price points when no affiliate-item prices are available."""
        basic = basic_factory(budget_end=Decimal(10), luxury_start=Decimal(100))
        budget_start, luxury_end = update_basic_price_points(basic)

        assert budget_start is None
        assert luxury_end is None

        assert basic.budget_end == Decimal(10)
        assert basic.luxury_start == Decimal(100)
