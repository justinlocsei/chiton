import os
import shutil
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export the favicon to a file'

    def add_arguments(self, parser):
        parser.add_argument('--target', type=str, help='The absolute path to the destination')

    def handle(self, *arg, **options):
        source = os.path.join(settings.CHITON_ROOT, 'core', 'static', 'core', 'images', 'favicon.ico')
        dest = options['target']

        requires_update = True
        if os.path.isfile(dest):
            requires_update = subprocess.call(['diff', source, dest]) != 0

        if requires_update:
            shutil.copy(source, dest)
            self.stdout.write('Favicon exported')
