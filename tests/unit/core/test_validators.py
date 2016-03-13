from django.core.exceptions import ValidationError
import pytest

from chiton.core import validators


class TestValidateLooseRange:

    def test_null_range(self):
        """It accepts a range lacking upper and lower bounds."""
        assert validators.validate_loose_range(None, None) is None

    def test_open_lower(self):
        """It accepts a range without a lower bound."""
        assert validators.validate_loose_range(None, 10) is None

    def test_open_upper(self):
        """It accepts a range without an upper bound."""
        assert validators.validate_loose_range(10, None) is None

    def test_valid_range(self):
        """It accepts a closed range where the lower is less than the upper."""
        assert validators.validate_loose_range(10, 20) is None

    def test_equal_range(self):
        """It accepts a range where the lower and upper bounds are identical."""
        assert validators.validate_loose_range(10, 10) is None

    def test_reversed_range(self):
        """It raises an error when the range is incorrectly ordered."""
        with pytest.raises(ValidationError):
            validators.validate_loose_range(11, 10)
