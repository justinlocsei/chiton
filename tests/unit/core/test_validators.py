from django.core.exceptions import ValidationError
import pytest

from chiton.core.validators import validate_range


class TestValidateRange:

    def test_null_range(self):
        """It requires a range with endpoints."""
        with pytest.raises(ValidationError):
            validate_range(None, None)

    def test_null_range_lower(self):
        """It requires a lower bound."""
        with pytest.raises(ValidationError):
            validate_range(None, 10)

    def test_null_range_upper(self):
        """It requires an upper bound."""
        with pytest.raises(ValidationError):
            validate_range(10, None)

    def test_valid_range(self):
        """It accepts a closed range where the lower is less than the upper."""
        assert validate_range(10, 20) is None

    def test_equal_range(self):
        """It accepts a range where the lower and upper bounds are identical."""
        assert validate_range(10, 10) is None

    def test_reversed_range(self):
        """It raises an error when the range is incorrectly ordered."""
        with pytest.raises(ValidationError):
            validate_range(11, 10)


class TestValidateRangeLoose:

    def test_null_range(self):
        """It accepts a range lacking upper and lower bounds."""
        assert validate_range(None, None, loose=True) is None

    def test_open_lower(self):
        """It accepts a range without a lower bound."""
        assert validate_range(None, 10, loose=True) is None

    def test_open_upper(self):
        """It accepts a range without an upper bound."""
        assert validate_range(10, None, loose=True) is None

    def test_valid_range(self):
        """It accepts a closed range where the lower is less than the upper."""
        assert validate_range(10, 20, loose=True) is None

    def test_equal_range(self):
        """It accepts a range where the lower and upper bounds are identical."""
        assert validate_range(10, 10, loose=True) is None

    def test_reversed_range(self):
        """It raises an error when the range is incorrectly ordered."""
        with pytest.raises(ValidationError):
            validate_range(11, 10, loose=True)
