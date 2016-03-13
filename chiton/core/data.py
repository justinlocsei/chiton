import os.path

from django.core import serializers

from chiton.core.exceptions import FilesystemError


def create_fixture(queryset, destination, natural_keys=False):
    """Create a fixture for a set of models.

    Args:
        queryset (django.db.models.query.QuerySet): A queryset of models
        destination (str): The absolute path to the destination fixture
        natural_keys (bool): Whether to use natural keys when creating the fixture

    Raises:
        chiton.core.exceptions.FilesystemError: If the fixture cannot be saved
    """
    fixtures_dir = os.path.dirname(destination)
    if not os.path.isdir(fixtures_dir):
        raise FilesystemError('No fixtures directory found at %s' % fixtures_dir)

    JSONSerializer = serializers.get_serializer('json')
    json_serializer = JSONSerializer()

    with open(destination, 'w') as fixture:
        json_serializer.serialize(
            queryset,
            stream=fixture,
            indent=4,
            use_natural_foreign_keys=natural_keys,
            use_natural_primary_keys=natural_keys
        )
