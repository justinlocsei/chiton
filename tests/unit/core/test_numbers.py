from decimal import Decimal

from chiton.core.numbers import format_float, price_to_integer


class TestFormatFloat:

    def test_precision(self):
        """It shows a float with arbitrary precision."""
        number = float(10.125)

        assert format_float(number, precision=1) == '10.1'
        assert format_float(number, precision=2) == '10.12'
        assert format_float(number, precision=3) == '10.125'
        assert format_float(number, precision=4) == '10.1250'

    def test_integer(self):
        """It shows a float as an integer if it only has trailing zeroes."""
        number = float(10.00)
        assert format_float(number) == '10'

    def test_trailing_zeroes(self):
        """It preserves trailing zeroes up to the given precision."""
        number = float(10.50)

        assert format_float(number, precision=1) == '10.5'
        assert format_float(number, precision=2) == '10.50'
        assert format_float(number, precision=3) == '10.500'


class TestPriceToInteger:

    def test_whole(self):
        """It converts whole decimal numbers to integer cents."""
        price = Decimal(10)
        assert price_to_integer(price) == 1000

    def test_fractional(self):
        """It converts fractional decimal numbers to integer cents."""
        price = Decimal('10.25')
        assert price_to_integer(price) == 1025

    def test_zero(self):
        """It converts a zero-dollar price to an integer."""
        price = Decimal(0)
        assert price_to_integer(price) == 0

    def test_null(self):
        """It converts an undefined price to an integer."""
        assert price_to_integer(None) is None
