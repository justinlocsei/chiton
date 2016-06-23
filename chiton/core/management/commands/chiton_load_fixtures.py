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

            if not fixture.is_needed():
                self.stdout.write('Skipping the %s fixture' % fixture.label)
                continue

            resolved.append({
                'file': file,
                'label': fixture.label,
                'models': fixture.queryset
            })

        labels = sorted([f['label'] for f in resolved])
        self.stdout.write('Loading fixtures:')
        for label in labels:
            self.stdout.write('  %s' % label)

        before_count = sum([f['models'].count() for f in resolved])
        files = [f['file'] for f in resolved]
        call_command('loaddata', *files)
        after_count = sum([f['models'].all().count() for f in resolved])

        model_delta = after_count - before_count
        self.stdout.write('New model count: %d' % model_delta)
