from django.contrib.auth.models import User
import pytest

from chiton.wintour.models import Person


@pytest.mark.django_db
class TestPerson:

    @pytest.fixture
    def john_doe(self):
        return User.objects.create_user('jdoe', 'jdoe@example.com')

    def test_full_name(self, john_doe):
        """It builds the person's full name from their first and last name."""
        person = Person.objects.create(first_name="John", last_name="Doe", user=john_doe)

        assert person.full_name == 'John Doe'

    def test_slug(self, john_doe):
        """It uses the person's full name as the slug."""
        person = Person.objects.create(first_name="John", last_name="Doe", user=john_doe)

        assert person.slug == 'john-doe'
