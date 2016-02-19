from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def ensure_superuser_exists(username, email, password):
    """Ensure that a superuser exists with the given information.

    If the user does not exist, they will be created.  If they alread exist,
    their information will be updated to match the given data.

    Args:
        username (str): The username for the superuser
        email (str): The user's email address
        password (str): The user's password

    Returns:
        django.contrib.auth.models.User: The superuser
        bool: Whether the user was created or modified

    Raises:
        django.core.exceptions.ValidationError: If the user cannot be saved
    """
    try:
        superuser = User.objects.get(username=username)
    except User.DoesNotExist:
        superuser = User.objects.create_superuser(username, email, password)
        try:
            superuser.full_clean()
        except ValidationError as e:
            superuser.delete()
            raise e
        return (superuser, True)

    before_fields = _get_superuser_fingerprint(superuser)

    superuser.email = email
    superuser.is_staff = True
    superuser.is_superuser = True
    if not superuser.check_password(password):
        superuser.set_password(password)

    superuser.full_clean()
    superuser.save()

    after_fields = _get_superuser_fingerprint(superuser)

    return (superuser, before_fields != after_fields)


def _get_superuser_fingerprint(user):
    """Get a fingerprint of a superuser from the value of their key fields."""
    fields = ['email', 'is_staff', 'is_superuser', 'password']
    return [getattr(user, field) for field in fields]
