import pytest

from chiton.wintour.models import Person


@pytest.mark.django_db
class TestPerson:

    def test_full_name(self):
        """It builds the person's full name from their first and last name."""
        person = Person.objects.create(first_name='John', last_name='Doe', email='test@example.com')
        assert person.full_name == 'John Doe'

    def test_full_name_partial(self):
        """It treats the first and last name as optional when making a full name."""
        first_only = Person.objects.create(first_name='John', email='test@example.com')
        last_only = Person.objects.create(last_name='Doe', email='test@example.com')
        anonymous = Person.objects.create(email='test@example.com')

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

    def test_email_blank(self):
        """It does not raise an error when the email address is blank."""
        person = Person.objects.create(first_name='John')
        assert person.email is None

    def test_str_full_name(self):
        """It uses the person's full name for display."""
        person = Person.objects.create(first_name='John', last_name='Doe', email='test@example.com')
        assert str(person) == 'John Doe'

    def test_ensure_exists_with_email_new(self):
        """It creates a person for a new email."""
        previous_emails = [p.email for p in Person.objects.all()]
        assert 'test@example.com' not in previous_emails

        person = Person.objects.ensure_exists_with_email('test@example.com')
        assert person.full_clean() is None

        assert person.email == 'test@example.com'
        assert person.pk

    def test_ensure_exists_with_email_existing(self):
        """It uses an existing person for an existing email."""
        person = Person.objects.create(email='test@example.com')
        ensured = Person.objects.ensure_exists_with_email('test@example.com')

        assert person.pk == ensured.pk
        assert person.email == 'test@example.com'
        assert ensured.email == 'test@example.com'

    def test_ensure_exists_with_email_normalized(self):
        """It uses the normalized form of the email address."""
        person = Person.objects.ensure_exists_with_email('test@MyExample.com')

        assert person.pk
        assert person.email == 'test@myexample.com'
