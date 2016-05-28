from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Update item stock'

    def add_arguments(self, parser):
        parser.add_argument(
            '--workers',
            action='store',
            dest='workers',
            default=2,
            type=int,
            help='The number of workers to use'
        )

    def handle(self, *arg, **options):
        call_command('chiton_refresh_affiliate_items', workers=options['workers'])
        call_command('chiton_update_basic_price_points')
