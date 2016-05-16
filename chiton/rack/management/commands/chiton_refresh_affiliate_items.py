from django.core.management.base import BaseCommand

from chiton.rack.affiliates.bulk import bulk_update_affiliate_item_details, bulk_update_affiliate_item_metadata
from chiton.rack.models import AffiliateItem


class Command(BaseCommand):
    help = 'Refresh the local API data for all affiliate items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--meta',
            action='store_true',
            dest='meta',
            default=False,
            help='Update the GUID and name of each item'
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
            target_noun = 'metadata' if options['meta'] else 'details'
            self.stdout.write('Updating %s for %d items with %d workers\n--' % (target_noun, total_count, options['workers']))

        if options['meta']:
            item_updater = bulk_update_affiliate_item_metadata
        else:
            item_updater = bulk_update_affiliate_item_details

        item_queue = item_updater(items, workers=options['workers'])

        while True:
            task = item_queue.get()
            item_queue.task_done()
            processed_count += 1

            if task['is_error']:
                self.stdout.write(self.style.ERROR('\n[!] %d/%d (%s)' % (processed_count, total_count, task['label'])))
                self.stdout.write(self.style.ERROR('--\n%s\n--\n' % task['details']))
            else:
                self.stdout.write('%d/%d (%s)' % (processed_count, total_count, task['label']))

            if processed_count == total_count:
                break

        item_queue.join()
        self.stdout.write('\nAll affiliate items updated!')
