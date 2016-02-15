from django.core.management.base import BaseCommand

from chiton.utils.users import ensure_superuser_exists


class Command(BaseCommand):
    help = "Ensure that a superuser exists"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, required=True)
        parser.add_argument("--password", type=str, required=True)
        parser.add_argument("--username", type=str, required=True)

    def handle(self, *arg, **options):
        email = options['email']
        password = options['password']
        username = options['username']

        superuser, modified = ensure_superuser_exists(username, email, password)

        if modified:
            self.stdout.write("User modified")
        else:
            self.stdout.write("User not modified")
