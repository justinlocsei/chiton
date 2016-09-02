import pytest

from chiton.wintour.models import Person


@pytest.mark.django_db
class TestPerson:

    def test_full_name(self):
        """It builds the person's full name from their first and last name."""
        person = Person.objects.create(first_name='John', last_name='Doe')
        assert person.full_name == 'John Doe'

    def test_full_name_partial(self):
        """It treats the first and last name as optional when making a full name."""
        first_only = Person.objects.create(first_name='John')
        last_only = Person.objects.create(last_name='Doe')
        anonymous = Person.objects.create()

        assert first_only.full_name == 'John'
        assert last_only.full_name == 'Doe'
        assert anonymous.full_name == ''

    def test_email(self):
        """It allows read/write access to the user's email."""
        person = Person.objects.create(email='user@example.com')
        assert person.email == 'user@example.com'

        person.email = 'user@example.org'
        assert person.email == 'user@example.org'

        person.save()
        person = Person.objects.get(pk=person.pk)
        assert person.email == 'user@example.org'

    def test_str_full_name(self):
        """It uses the person's full name for display."""
        person = Person.objects.create(first_name='John', last_name='Doe')
        assert str(person) == 'John Doe'
