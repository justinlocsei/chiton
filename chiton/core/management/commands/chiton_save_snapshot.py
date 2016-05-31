from django.core.management import call_command
from django.core.management.base import BaseCommand

# App labels to exclude when dumping data
EXCLUSIONS = ['admin', 'sessions']


class Command(BaseCommand):
    help = 'Save a snapshot of all data to a file'

    def add_arguments(self, parser):
        parser.add_argument('destination', type=str, help='The absolute path to the snapshot file')

    def handle(self, *arg, **options):
        with open(options['destination'], 'w') as snapshot:
            call_command('dumpdata', exclude=EXCLUSIONS, stdout=snapshot)
