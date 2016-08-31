import pytest

from chiton.wintour.models import Person


@pytest.mark.django_db
class TestPerson:

    def test_full_name(self):
        """It builds the person's full name from their first and last name."""
        person = Person.objects.create(first_name='John', last_name='Doe')
        assert person.full_name == 'John Doe'

    def test_str_full_name(self):
        """It uses the person's full name for display."""
        person = Person.objects.create(first_name='John', last_name='Doe')
        assert str(person) == 'John Doe'
