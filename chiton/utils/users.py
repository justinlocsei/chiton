from django.contrib.auth.models import User


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

    Raises:
        django.core.exceptions.ValidationError: If the user cannot be saved
    """
    try:
        superuser = User.objects.get(username=username)
    except User.DoesNotExist:
        superuser = User.objects.create_superuser(username, email, password)
    else:
        superuser.email = email
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.set_password(password)

    superuser.full_clean()
    superuser.save()

    return superuser
