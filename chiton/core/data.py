import os.path

from django.core import serializers

from chiton.core.exceptions import FilesystemError


def create_fixture(queryset, label, app, natural_keys=False):
    """Create a fixture for a set of models.

    Args:
        queryset (django.db.models.query.QuerySet): A queryset of models
        label (str): An arbitrary label for the fixture's file name
        app (str): The dotted-path name of the app
        natural_keys (bool): Whether to use natural keys when creating the fixture

    Returns:
        str: The path to the created fixture

    Raises:
        chiton.core.exceptions.FilesystemError: If the fixture cannot be saved
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    app_dir = os.path.join(root_dir, app.replace('.', os.path.sep))
    fixtures_dir = os.path.join(app_dir, 'fixtures')

    if not os.path.isdir(fixtures_dir):
        raise FilesystemError('No fixtures directory found at %s' % fixtures_dir)

    JSONSerializer = serializers.get_serializer('json')
    json_serializer = JSONSerializer()

    fixture_file = os.path.join(fixtures_dir, '%s.json' % label)
    with open(fixture_file, 'w') as fixture:
        json_serializer.serialize(queryset,
            stream=fixture,
            indent=4,
            use_natural_foreign_keys=natural_keys,
            use_natural_primary_keys=natural_keys)

    return fixture_file
