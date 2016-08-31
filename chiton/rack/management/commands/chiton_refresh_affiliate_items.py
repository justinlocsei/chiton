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
        items = AffiliateItem.objects.all().order_by('pk').select_related('network')
        total_count = items.count()

        if total_count == 0:
            self.stdout.write('No affiliate items exist')
            return
        else:
            target_noun = 'metadata' if options['meta'] else 'details'
            self.stdout.write('Updating %s for %d items with %d workers\n--' % (target_noun, total_count, options['workers']))

        if options['meta']:
            create_batch_job = bulk_update_affiliate_item_metadata
        else:
            create_batch_job = bulk_update_affiliate_item_details

        batch_job = create_batch_job(items, workers=options['workers'])
        error_count = 0
        failed_updates = []

        item_labels = {}
        for item in items:
            item_labels[item.pk] = '%s: %s' % (item.network.name, item.name)

        for index, result in enumerate(batch_job.run()):
            label = item_labels[result.item_id]
            if result.is_error:
                error_count += 1
                self.stderr.write(self.style.ERROR('\n[!] %d/%d (%s)' % (index + 1, total_count, label)))
                self.stderr.write(self.style.ERROR('--\n%s\n--\n' % result.details))
                failed_updates.append(label)
            else:
                self.stdout.write('%d/%d (%s)' % (index + 1, total_count, label))

        if error_count:
            self.stderr.write(self.style.ERROR('\nUpdated %d/%d items' % (total_count - error_count, total_count)))
            self.stderr.write(self.style.ERROR('%d items could not be updated' % error_count))
            for failed_update in failed_updates:
                self.stderr.write(self.style.ERROR('* %s' % failed_update))
        else:
            self.stdout.write(self.style.SUCCESS('\nUpdated all %d items' % (total_count)))
