import os

from django.core.management import call_command
from django.core.management.base import BaseCommand

from chiton.utils.network import resolve_binding


class Command(BaseCommand):
    help = "Run a development server on an address and port set by environment variables"

    def handle(self, *arg, **options):
        address = os.environ.get("CHITON_SERVER_ADDRESS", "")
        port = os.environ.get("CHITON_SERVER_PORT", "")

        binding = resolve_binding(address, port=port)
        call_command("runserver", binding)
