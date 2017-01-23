from django.core.management.base import BaseCommand

from chiton.rack.affiliates.bulk import prune_affiliate_items
from chiton.rack.models import AffiliateItem


class Command(BaseCommand):
    help = 'Prune invalid affiliate items'

    def handle(self, *arg, **options):
        items = AffiliateItem.objects.all().order_by('pk').select_related('network')

        total_items = items.count()
        current_item = 0
        pruned_items = []

        for item_name, network_name, was_pruned in prune_affiliate_items(items):
            current_item += 1
            progress = '%d/%d' % (current_item, total_items)
            display_name = '%s (%s)' % (item_name, network_name)

            if was_pruned:
                pruned_items.append(display_name)
                self.stdout.write(self.style.SUCCESS('%s [PRUNE] %s' % (progress, display_name)))
            else:
                self.stdout.write('%s [SKIP] %s' % (progress, display_name))

        self.stdout.write('\n')
        if pruned_items:
            self.stdout.write('The following items were pruned:')
            for pruned_item in sorted(pruned_items):
                self.stdout.write('  - %s' % pruned_item)
        else:
            self.stdout.write('No items were pruned')
