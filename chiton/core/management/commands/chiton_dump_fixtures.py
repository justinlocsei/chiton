from django.core.management.base import BaseCommand

from chiton.core.fixtures import load_fixtures


class Command(BaseCommand):
    help = 'Create fixture files for all core data'

    def handle(self, *arg, **options):
        for fixture in load_fixtures():
            output = fixture.export()
            self.stdout.write('A %s fixture was created at %s' % (fixture.label, output))
