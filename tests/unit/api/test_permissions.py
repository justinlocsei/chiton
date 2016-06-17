from django.contrib.auth.models import Group, User
import pytest

from chiton.api.permissions import bind_user_to_group, enforce_auth_token, grant_group_permission
from chiton.closet.models import Color


@pytest.mark.django_db
class TestBindUserToGroup:

    @pytest.fixture
    def group(self):
        return Group.objects.create(name="Test Group")

    def test_creates_user(self, group):
        """It creates a user with the given username when they do not exist."""
        user, created = bind_user_to_group('tester', group)

        assert user.username == 'tester'
        assert created

    def test_skips_user_creation(self, group):
        """It does not create a user when they already exist."""
        user_one, created_one = bind_user_to_group('tester', group)
        user_two, created_two = bind_user_to_group('tester', group)

        assert user_one == user_two
        assert created_one
        assert not created_two

    def test_adds_user_to_group(self, group):
        """It adds the user to the group if they are not a member."""
        user = User.objects.create_user('tester')
        assert user.groups.count() == 0

        user, added = bind_user_to_group('tester', group)
        assert user.groups.count() == 1
        assert group in user.groups.all()
        assert added

    def test_skips_user_addition(self, group):
        """It does not re-add the user to the group if they are a member."""
        user = User.objects.create_user('tester')
        user.groups.add(group)

        user, added = bind_user_to_group('tester', group)
        assert not added


@pytest.mark.django_db
class TestEnforceAuthToken:

    @pytest.fixture
    def user(self):
        return User.objects.create_user('tester')

    def test_creates_token(self, user):
        """It creates a token for a user when they lack one."""
        created = enforce_auth_token(user, 'token')

        assert created
        assert user.auth_token.key == 'token'

    def test_modifies_token(self, user):
        """It modifies a token if the key value is different."""
        enforce_auth_token(user, 'first')
        assert user.auth_token.key == 'first'

        updated = enforce_auth_token(user, 'second')
        assert user.auth_token.key == 'second'
        assert updated

    def test_skips_token(self, user):
        """It does nothing if the token's key matches the given value."""
        created = enforce_auth_token(user, 'first')
        updated = enforce_auth_token(user, 'first')

        assert created
        assert not updated


@pytest.mark.django_db
class TestGrantGroupPermission:

    @pytest.fixture
    def group(self):
        return Group.objects.create(name='Test Group')

    def test_adds_permission(self, group):
        """It adds a permission when it does not exist."""
        added = grant_group_permission(group, Color, add=True)

        assert added
        assert group.permissions.count() == 1

    def test_skips_permission(self, group):
        """It does not not re-add existing permissions."""
        added = grant_group_permission(group, Color, add=True)
        updated = grant_group_permission(group, Color, add=True)

        assert added
        assert not updated

        assert group.permissions.count() == 1

    def test_skips_default(self, group):
        """It does nothing when the permission type is not specified."""
        added = grant_group_permission(group, Color)
        assert not added

    def test_variants(self, group):
        """It handles add, change, and delete permissions."""
        add_add = grant_group_permission(group, Color, add=True)
        assert add_add
        assert group.permissions.count() == 1

        add_change = grant_group_permission(group, Color, change=True)
        assert add_change
        assert group.permissions.count() == 2

        add_delete = grant_group_permission(group, Color, delete=True)
        assert add_delete
        assert group.permissions.count() == 3

        assert set(group.permissions.all().values_list('codename', flat=True)) == set(['add_color', 'change_color', 'delete_color'])
