import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run a development server on a port set by an environment variable"

    def handle(self, *arg, **kwargs):
        call_command("runserver", os.environ.get("CHITON_SERVER_PORT"))
