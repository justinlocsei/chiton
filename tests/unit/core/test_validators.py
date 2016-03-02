from unittest import TestCase

from django.core.exceptions import ValidationError

from chiton.core import validators


class ValidateLooseRangeTestCase(TestCase):

    def test_null_range(self):
        """It accepts a range lacking upper and lower bounds."""
        self.assertIsNone(validators.validate_loose_range(None, None))

    def test_open_lower(self):
        """It accepts a range without a lower bound."""
        self.assertIsNone(validators.validate_loose_range(None, 10))

    def test_open_upper(self):
        """It accepts a range without an upper bound."""
        self.assertIsNone(validators.validate_loose_range(10, None))

    def test_valid_range(self):
        """It accepts a closed range where the lower is less than the upper."""
        self.assertIsNone(validators.validate_loose_range(10, 20))

    def test_equal_range(self):
        """It accepts a range where the lower and upper bounds are identical."""
        self.assertIsNone(validators.validate_loose_range(10, 10))

    def test_reversed_range(self):
        """It raises an error when the range is incorrectly ordered."""
        with self.assertRaises(ValidationError):
            validators.validate_loose_range(11, 10)
