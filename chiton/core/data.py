import os.path

from django.conf import settings
from django.core import serializers

from chiton.core.exceptions import FilesystemError


class Fixture:
    """A representation of a fixture for a single application model."""

    def __init__(self, app, label, queryset, use_natural_keys=True):
        """Create a new fixture.

        Args:
            app (django.apps.AppConfig): An application's configuration instance
            label (str): A label for the fixture
            queryset (django.db.models.query.QuerySet): A queryset of models

        Keyword Args:
            use_natural_keys (bool): Whether to use natural keys when creating the fixture

        """
        self.app = app
        self.label = label
        self.queryset = queryset
        self.use_natural_keys = use_natural_keys

    def find(self):
        """Return the absolute path to the fixture's file.

        Returns:
            str: The path to the fixture file
        """
        app_paths = [path for path in self.app.name.split('.') if path != 'chiton']
        app_dir = os.path.join(settings.CHITON_ROOT, *app_paths)

        return os.path.join(app_dir, 'fixtures', '%s.json' % self.label)

    def export(self):
        """Write the fixture data to a file.

        Returns:
            str: The path to the saved fixture file

        Raises:
            chiton.core.exceptions.FilesystemError: If the fixture cannot be saved
        """
        destination = self.find()
        fixtures_dir = os.path.dirname(destination)
        if not os.path.isdir(fixtures_dir):
            raise FilesystemError('No fixtures directory found at %s' % fixtures_dir)

        JSONSerializer = serializers.get_serializer('json')
        json_serializer = JSONSerializer()

        with open(destination, 'w') as fixture:
            json_serializer.serialize(
                self.queryset,
                stream=fixture,
                indent=4,
                use_natural_foreign_keys=self.use_natural_keys,
                use_natural_primary_keys=self.use_natural_keys
            )

        return destination
