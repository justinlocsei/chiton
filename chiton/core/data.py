import os.path

from django.conf import settings
from django.core import serializers
from inflection import underscore
import voluptuous as V

from chiton.core.exceptions import FilesystemError, FormatError


def make_data_shape_creator(schema):
    """Create a function that validates a dict according to a schema.

    Args:
        schema (dict): A Voluptuous schema

    Returns:
        function: A function that creates and validates a dict according to the schema
    """
    def validate(data):
        try:
            V.Schema(schema)(data)
        except V.MultipleInvalid as e:
            raise FormatError('Invalid data format: %s' % e)
        else:
            return data

    return validate


class Fixture:
    """A representation of a fixture for a single application model."""

    def __init__(self, model_class, queryset):
        """Create a new fixture.

        Args:
            model_class (django.db.models.Model): The model class for the fixture
            queryset (django.db.models.query.QuerySet): A queryset of models
        """
        self.model_class = model_class
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
                use_natural_foreign_keys=True,
                use_natural_primary_keys=True
            )

        return destination
