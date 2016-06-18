import pytest
import voluptuous as V

from chiton.core.schema import define_data_shape, NumberInRange, OneOf
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

    def test_validation_disabled_global(self):
        """It can disable validation by default at a global level."""
        create_and_validate = define_data_shape({'age': int})
        create_and_ignore = define_data_shape({'age': int}, validated=False)

        with pytest.raises(FormatError):
            create_and_validate({'age': '10'})

        ignored = create_and_ignore({'age': '10'})
        assert ignored['age'] == '10'

    def test_validation_disabled_local(self):
        """It can disable validation by default on a per-call basis."""
        create_and_validate = define_data_shape({'age': int})
        create_and_ignore = define_data_shape({'age': int}, validated=False)

        with pytest.raises(FormatError):
            create_and_ignore({'age': '10'}, validate=True)

        ignored = create_and_validate({'age': '10'}, validate=False)
        assert ignored['age'] == '10'

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

    def test_errors_fields(self):
        """It exposes per-field errors."""
        def IsConstant(constant):
            def validator(v):
                if v != constant:
                    raise V.Invalid('%s must equal %s' % (v, constant))
            return validator

        shape = define_data_shape({
            'first_name': IsConstant('John'),
            'last_name': IsConstant('Doe')
        })

        with pytest.raises(FormatError) as error:
            shape({
                'first_name': 'Jane',
                'last_name': 'Dear'
            })

        assert 'must equal' in str(error)
        assert error.value.fields['first_name'] == 'Jane must equal John'
        assert error.value.fields['last_name'] == 'Dear must equal Doe'

    def test_errors_fields_nested(self):
        """It uses a dotted path for errors with nested fields."""
        shape = define_data_shape({
            'first': {
                'second': {
                    'value': int
                }
            }
        })

        with pytest.raises(FormatError) as error:
            shape({
                'first': {
                    'second': {
                        'value': 'str'
                    }
                }
            })

        assert 'first.second.value' in error.value.fields

    def test_errors_fields_arrays(self):
        """It uses indices for nested array errors."""
        shape = define_data_shape({'list': [str]})

        with pytest.raises(FormatError) as error:
            shape({
                'list': ['a', 1, 'b']
            })

        assert 'list.1' in error.value.fields


class TestNumberInRange:

    def test_valid(self):
        """It accepts numbers in a given range."""
        schema = V.Schema({'value': NumberInRange(10, 20)})

        assert schema({'value': 15})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': 0})

    def test_valid_inclusive(self):
        """It is inclusive on both ends of the range."""
        schema = V.Schema({'value': NumberInRange(10, 20)})

        assert schema({'value': 10})
        assert schema({'value': 20})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': 9})
        with pytest.raises(V.MultipleInvalid):
            schema({'value': 21})


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

    def test_multiple(self):
        """It can validate lists when operating in multiple mode."""
        schema = V.Schema({'value': OneOf(['a', 'b'], multiple=True)})

        assert schema({'value': ['a']})
        assert schema({'value': ['a', 'b']})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': ['c']})

    def test_multiple_invalid(self):
        """It requires every value in a list to be valid in multiple mode."""
        schema = V.Schema({'value': OneOf(['a', 'b'], multiple=True)})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': ['a', 'b', 'c']})

    def test_multiple_empty(self):
        """It counts empty lists as invalid in multiple mode."""
        schema = V.Schema({'value': OneOf(['a'], multiple=True)})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': []})

    def test_lazy(self):
        """It accepts a function that lazily provides a list of choices."""
        choice_list = []

        def choices():
            choice_list.append(len(choice_list) + 1)
            return choice_list

        schema = V.Schema({'value': OneOf(choices)})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': 2})

        assert schema({'value': 2})

    def test_lazy_multiple(self):
        """It accepts lazy choice lists in multiple mode."""
        schema = V.Schema({'value': OneOf(lambda: [1, 2], multiple=True)})

        assert schema({'value': [1, 2]})

        with pytest.raises(V.MultipleInvalid):
            schema({'value': [1, 2, 3]})
