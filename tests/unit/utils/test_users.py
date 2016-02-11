from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from chiton.utils import users


class EnsureSuperuserExistsTestCase(TestCase):

    def test_creates_new(self):
        """It creates a new superuser if one does not exist."""
        superusers = User.objects.filter(is_superuser=True)
        self.assertEqual(superusers.count(), 0)

        superuser = users.ensure_superuser_exists("admin", "admin@example.com", "password")
        self.assertIsNotNone(superuser.pk)
        self.assertEqual(superuser.username, "admin")
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("password"))
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

        superusers = User.objects.filter(is_superuser=True)
        self.assertEqual(superusers.count(), 1)

    def test_updates_existing(self):
        """It updates an existing user if the superuser already exists."""
        user = User.objects.create_user("user", "user@example.com", "password")
        superuser = users.ensure_superuser_exists("user", "superuser@example.com", "newpassword")

        self.assertEqual(user.pk, superuser.pk)
        self.assertEqual(superuser.email, "superuser@example.com")
        self.assertTrue(superuser.check_password("newpassword"))

    def test_promotes_user(self):
        """It ensures that an existing user is made a superuser."""
        user = User.objects.create_user("user", "user@example.com", "password")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        superuser = users.ensure_superuser_exists("user", "superuser@example.com", "newpassword")
        self.assertEqual(user.pk, superuser.pk)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_validates_user(self):
        """It raises an error when trying to save an invalid user."""
        with self.assertRaises(ValidationError):
            users.ensure_superuser_exists("user", "invalid@email", "newpassword")
