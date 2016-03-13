import os.path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from chiton.core.fixtures import load_fixtures


class Command(BaseCommand):
    help = 'Load all application fixtures'

    def handle(self, *arg, **options):
        for fixture in load_fixtures():
            file = fixture.find()
            if not os.path.isfile(file):
                raise CommandError('The %s fixture could not be located' % fixture.label)

            self.stdout.write('Loading %s fixture...' % fixture.label)
            call_command('loaddata', file)
