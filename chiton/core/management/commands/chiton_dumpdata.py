from django.core.management.base import BaseCommand

from chiton.closet.apps import Config as Closet
from chiton.closet.models import Formality, Style
from chiton.core.data import create_fixture


class Command(BaseCommand):
    help = 'Create fixtures of all core data'

    def handle(self, *arg, **options):
        fixtures = [
            {
                'app': Closet,
                'label': 'formalities',
                'natural_keys': True,
                'queryset': Formality.objects.all()
            },
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
