import pytest
import voluptuous as V

from chiton.utils.validation import OneOf


class TestOneOf:

    def test_choice_list(self):
        """It ensures that a value is in a choice list."""
        schema = V.Schema({'value': OneOf(['a', 'b'])})

        assert schema({'value': 'a'})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': 'c'})

    def test_error_normalization(self):
        """It ensures that error messages can handle non-string choice lists."""
        schema = V.Schema({'value': OneOf([1, 2])})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': 3})

    def test_list(self):
        """It does not treat lists as scalars."""
        schema = V.Schema({'value': OneOf(['a', 'b'])})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': ['a']})
