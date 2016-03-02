from django.core.management.base import BaseCommand

from chiton.closet.apps import Config
from chiton.core.data import create_fixture


class Command(BaseCommand):
    help = 'Create fixtures from the core closet model data'

    def handle(self, *arg, **options):
        fixtures = []

        for fixture in fixtures:
            file_path = create_fixture(
                fixture['queryset'],
                fixture['label'],
                Config.name,
                natural_keys=fixture['natural_keys'])
            self.stdout.write('A %s fixture was created at %s' % (fixture['label'], file_path))
