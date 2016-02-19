from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from chiton.utils import users


class EnsureSuperuserExistsTestCase(TestCase):

    def test_creates_new(self):
        """It creates a new superuser if one does not exist."""
        superusers = User.objects.filter(is_superuser=True)
        self.assertEqual(superusers.count(), 0)

        superuser, updated = users.ensure_superuser_exists('admin', 'admin@example.com', 'password')
        self.assertIsNotNone(superuser.pk)
        self.assertEqual(superuser.username, 'admin')
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertTrue(superuser.check_password('password'))
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

        superusers = User.objects.filter(is_superuser=True)
        self.assertEqual(superusers.count(), 1)
        self.assertTrue(updated)

    def test_updates_existing(self):
        """It updates an existing user if the superuser already exists."""
        user = User.objects.create_user('user', 'user@example.com', 'password')
        superuser, updated = users.ensure_superuser_exists('user', 'superuser@example.com', 'newpassword')

        self.assertEqual(user.pk, superuser.pk)
        self.assertEqual(superuser.email, 'superuser@example.com')
        self.assertTrue(superuser.check_password('newpassword'))
        self.assertTrue(updated)

    def test_promotes_user(self):
        """It ensures that an existing user is made a superuser."""
        user = User.objects.create_user('user', 'user@example.com', 'password')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        superuser, updated = users.ensure_superuser_exists('user', 'superuser@example.com', 'newpassword')
        self.assertEqual(user.pk, superuser.pk)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(updated)

    def test_preserves_existing(self):
        """It does not modify a superuser that matches the given data."""
        user = User.objects.create_superuser('user', 'superuser@example.com', 'password')
        superuser, updated = users.ensure_superuser_exists('user', 'superuser@example.com', 'password')

        self.assertEqual(user.pk, superuser.pk)
        self.assertFalse(updated)

    def test_validates_user_new(self):
        """It does not create a user when given invalid data."""
        with self.assertRaises(ValidationError):
            users.ensure_superuser_exists('user', 'invalid@email', 'newpassword')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='user')

    def test_validates_user_existing(self):
        """It does not modify an existing user when given invalid data."""
        User.objects.create_user('user', 'user@example.com', 'password')

        with self.assertRaises(ValidationError):
            users.ensure_superuser_exists('user', 'invalid@email', 'newpassword')

        user = User.objects.get(username='user')
        self.assertEqual(user.email, 'user@example.com')
