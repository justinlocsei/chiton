from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token


def grant_group_permission(group, model_class, add=False, change=False, delete=False):
    """Grant a model permission to a group.

    Args:
        group (django.contrib.auth.models.Group): A group instance
        model_class (django.db.models.Model): A model class

    Keyword Args:
        add (bool): Whether to grant add privileges
        change (bool): Whether to grant change privileges
        delete (bool): Whether to grant delete privileges

    Returns:
        bool: Whether the permission was added
    """
    granted = False
    content_type = ContentType.objects.get_for_model(model_class)

    prefixes = ['add' * add, 'change' * change, 'delete' * delete]
    prefixes = [prefix for prefix in prefixes if prefix]
    for prefix in prefixes:
        permission = Permission.objects.get(content_type=content_type, codename__startswith='%s_' % prefix)

        try:
            group.permissions.get(pk=permission.pk)
        except ObjectDoesNotExist:
            group.permissions.add(permission)
            granted = True

    return granted


def bind_user_to_group(username, group):
    """Ensure that a user exists and is a member of a group.

    Args:
        username (str): The name of the user
        group (django.contrib.auth.models.Group): A group instance

    Returns:
        django.contrib.auth.models.User: The user instance
        bool: Whether the user was added
    """
    bound = False

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = User.objects.create_user(username)
        bound = True

    try:
        user.groups.get(pk=group.pk)
    except ObjectDoesNotExist:
        user.groups.add(group)
        bound = True

    return (user, bound)


def enforce_auth_token(user, token):
    """Ensure that a user has a given authentication token.

    Args:
        user (django.contrib.auth.models.User): A user instance
        token (str): The desired authentication token

    Returns:
        bool: Whether the token was updated
    """
    try:
        auth_token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        auth_token = None
        update = True
    else:
        update = auth_token.key != token

    if update and auth_token:
        auth_token.delete()
    if update:
        Token.objects.create(user=user, key=token)

    return update
