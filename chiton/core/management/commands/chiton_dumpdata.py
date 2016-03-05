from django.core.management.base import BaseCommand

from chiton.closet.apps import Config as Closet
from chiton.closet.models import Style
from chiton.core.data import create_fixture


class Command(BaseCommand):
    help = 'Create fixtures from the core closet model data'

    def handle(self, *arg, **options):
        fixtures = [
            {
                'app': Closet,
                'label': 'styles',
                'natural_keys': True,
                'queryset': Style.objects.all()
            }
        ]

        for fixture in fixtures:
            file_path = create_fixture(
                fixture['queryset'],
                fixture['label'],
                fixture['app'].name,
                natural_keys=fixture['natural_keys'])
            self.stdout.write('A %s fixture was created at %s' % (fixture['label'], file_path))
