import pytest
import voluptuous as V

from chiton.core.schema import define_data_shape, OneOf
from chiton.core.exceptions import FormatError


class TestDefineDataShape:

    def test_dict(self):
        """It creates a function that returns a given dict."""
        create_person = define_data_shape({V.Required('name'): str})
        person = create_person({'name': 'Tester'})

        assert isinstance(person, dict)
        assert person['name'] == 'Tester'

    def test_dict_unmodified(self):
        """It does not modify a valid dict."""
        create_person = define_data_shape({V.Required('age'): int})
        original = {'age': 10}
        validated = create_person({'age': 10})

        assert original == validated

    def test_validation(self):
        """It creates a function that validates its argument."""
        create_person = define_data_shape({V.Required('bmi'): int})

        with pytest.raises(FormatError) as validation_error:
            create_person({'bmi': '10'})

        assert 'bmi' in str(validation_error)

    def test_defaults(self):
        """It accepts default values."""
        create_person = define_data_shape(
            {'name': str},
            {'name': 'John'}
        )

        john = create_person()
        jane = create_person({'name': 'Jane'})

        assert john['name'] == 'John'
        assert jane['name'] == 'Jane'

    def test_defaults_persistence(self):
        """It does not persist default values."""
        create_person = define_data_shape(
            {'name': str},
            {'name': 'John'}
        )

        jane = create_person({'name': 'Jane'})
        john = create_person()

        assert john['name'] == 'John'
        assert jane['name'] == 'Jane'


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
