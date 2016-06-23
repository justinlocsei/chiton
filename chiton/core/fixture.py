import os.path

from django.conf import settings
from django.core import serializers
from inflection import underscore

from chiton.core.exceptions import FilesystemError


class Fixture:
    """A representation of a fixture for a single application model."""

    def __init__(self, model_class, queryset=None, initial=False, requires=[], fields=None):
        """Create a new fixture.

        Args:
            model_class (django.db.models.Model): The model class for the fixture
            queryset (django.db.models.query.QuerySet): A queryset of models

        Keyword Args:
            initial (bool): Whether the fixture should only be run to initialize data
            requires (list[django.db.models.model]): All model classes required by the fixture
            fields (list[str]): A list of field names to serialize
        """
        self.model_class = model_class
        self.initial = initial
        self.requires = requires
        self.fields = fields

        if queryset is None:
            self.queryset = model_class.objects.all()
        else:
            self.queryset = queryset

        self.label = underscore(model_class.__name__)

    def find(self):
        """Return the absolute path to the fixture's file.

        Returns:
            str: The path to the fixture file
        """
        app_name = self.model_class._meta.app_config.name
        app_paths = [path for path in app_name.split('.') if path != 'chiton']
        app_dir = os.path.join(settings.CHITON_ROOT, *app_paths)

        return os.path.join(app_dir, 'fixtures', '%s.json' % self.label)

    def is_needed(self):
        """Determine whether the fixture is needed.

        A fixture will only ever be unneeded if it is an initial fixture and
        models of the fixture's type are present.

        Returns:
            bool: Whether the fixture is needed
        """
        if self.initial:
            return not self.queryset.count()
        else:
            return True

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
            serialize_kwargs = {
                'stream': fixture,
                'indent': 4,
                'use_natural_foreign_keys': True,
                'use_natural_primary_keys': True
            }
            if self.fields:
                serialize_kwargs['fields'] = self.fields

            json_serializer.serialize(self.queryset, **serialize_kwargs)

        return destination
