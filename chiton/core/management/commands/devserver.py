import os

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run a development server on a and address port set by environment variables"

    def handle(self, *arg, **kwargs):
        address = os.environ.get("CHITON_SERVER_ADDRESS")
        port = os.environ.get("CHITON_SERVER_PORT")

        bindings = [address, port]
        binding = ":".join([str(b) for b in bindings if b])

        call_command("runserver", binding)
