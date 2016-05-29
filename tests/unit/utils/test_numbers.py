from chiton.utils.numbers import format_float


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
