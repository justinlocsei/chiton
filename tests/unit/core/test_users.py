from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import pytest

from chiton.core import users


@pytest.mark.django_db
class TestEnsureSuperuserExists:

    def test_creates_new(self):
        """It creates a new superuser if one does not exist."""
        superusers = User.objects.filter(is_superuser=True)
        assert superusers.count() == 0

        superuser, updated = users.ensure_superuser_exists('admin', 'admin@example.com', 'password')
        assert superuser.pk is not None
        assert superuser.username == 'admin'
        assert superuser.email == 'admin@example.com'
        assert superuser.check_password('password')
        assert superuser.is_superuser
        assert superuser.is_staff

        superusers = User.objects.filter(is_superuser=True)
        assert superusers.count() == 1
        assert updated

    def test_updates_existing(self):
        """It updates an existing user if the superuser already exists."""
        user = User.objects.create_user('user', 'user@example.com', 'password')
        superuser, updated = users.ensure_superuser_exists('user', 'superuser@example.com', 'newpassword')

        assert user.pk == superuser.pk
        assert superuser.email == 'superuser@example.com'
        assert superuser.check_password('newpassword')
        assert updated

    def test_promotes_user(self):
        """It ensures that an existing user is made a superuser."""
        user = User.objects.create_user('user', 'user@example.com', 'password')
        assert not user.is_staff
        assert not user.is_superuser

        superuser, updated = users.ensure_superuser_exists('user', 'superuser@example.com', 'newpassword')
        assert user.pk == superuser.pk
        assert superuser.is_staff
        assert superuser.is_superuser
        assert updated

    def test_preserves_existing(self):
        """It does not modify a superuser that matches the given data."""
        user = User.objects.create_superuser('user', 'superuser@example.com', 'password')
        superuser, updated = users.ensure_superuser_exists('user', 'superuser@example.com', 'password')

        assert user.pk == superuser.pk
        assert not updated

    def test_validates_user_new(self):
        """It does not create a user when given invalid data."""
        with pytest.raises(ValidationError):
            users.ensure_superuser_exists('user', 'invalid@email', 'newpassword')

        with pytest.raises(User.DoesNotExist):
            User.objects.get(username='user')

    def test_validates_user_existing(self):
        """It does not modify an existing user when given invalid data."""
        User.objects.create_user('user', 'user@example.com', 'password')

        with pytest.raises(ValidationError):
            users.ensure_superuser_exists('user', 'invalid@email', 'newpassword')

        user = User.objects.get(username='user')
        assert user.email == 'user@example.com'
