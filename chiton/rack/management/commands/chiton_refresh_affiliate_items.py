from django.core.management.base import BaseCommand

from chiton.rack.affiliates.data import refresh_affiliate_items
from chiton.rack.models import AffiliateItem


class Command(BaseCommand):
    help = 'Refresh the local API data for all affiliate items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            dest='full_refresh',
            default=False,
            help='Perform a full refresh that updates the GUID and name'
        )

        parser.add_argument(
            '--workers',
            action='store',
            dest='workers',
            default=2,
            type=int,
            help='The number of workers to use'
        )

    def handle(self, *arg, **options):
        items = AffiliateItem.objects.all().order_by('pk')
        total_count = items.count()
        processed_count = 0

        if total_count == 0:
            self.stdout.write('No affiliate items exist')
            return
        else:
            self.stdout.write('Processing %d items with %d workers\n--' % (total_count, options['workers']))

        item_queue = refresh_affiliate_items(items,
            full=options['full_refresh'],
            workers=options['workers']
        )

        while True:
            message = item_queue.get()
            item_queue.task_done()

            processed_count += 1
            self.stdout.write('Updating: %d/%d (%s)' % (processed_count, total_count, message['item_name']))
            if processed_count == total_count:
                break

        item_queue.join()
        self.stdout.write('\nAll affiliate items updated!')
