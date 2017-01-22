from django.core.management.base import BaseCommand

from chiton.wintour.models import Person


class Command(BaseCommand):
    help = 'Clear all encrypted data'

    def handle(self, *arg, **options):
        cleared_emails = Person.objects.clear_email_addresses()

        if cleared_emails:
            self.stdout.write('Updated encrypted data')
        else:
            self.stdout.write('No encrypted data was modified')
