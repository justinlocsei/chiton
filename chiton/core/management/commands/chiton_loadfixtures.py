import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from chiton.core.fixtures import load_fixtures


class Command(BaseCommand):
    help = 'Load all application fixtures'

    def handle(self, *arg, **options):
        resolved = []

        for fixture in load_fixtures():
            file = fixture.find()
            if not os.path.isfile(file):
                raise CommandError('The %s fixture could not be located' % fixture.label)
            resolved.append((file, fixture.label))

        labels = sorted([f[1] for f in resolved])
        self.stdout.write('Loading fixtures:')
        for label in labels:
            self.stdout.write('  %s' % label)

        files = [f[0] for f in resolved]
        call_command('loaddata', *files)
