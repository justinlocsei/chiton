import pytest
import voluptuous as V

from chiton.core.data import make_data_shape_creator
from chiton.core.exceptions import FormatError


class TestMakeDataShapeCreator:

    def test_dict(self):
        """It creates a function that returns a given dict."""
        create_person = make_data_shape_creator({V.Required('name'): str})
        person = create_person({'name': 'Tester'})

        assert isinstance(person, dict)
        assert person['name'] == 'Tester'

    def test_validation(self):
        """It creates a function that validates its argument."""
        create_person = make_data_shape_creator({V.Required('bmi'): int})

        with pytest.raises(FormatError) as validation_error:
            create_person({'bmi': '10'})

        assert 'bmi' in str(validation_error)
