from django.core.management.base import BaseCommand

from chiton.rack.pricing import update_basic_price_points
from chiton.runway.models import Basic


class Command(BaseCommand):
    help = 'Update the price points for all basics'

    def handle(self, *arg, **options):
        basics = Basic.objects.all().order_by('name')

        for basic in basics:
            previous_budget = basic.budget_end
            previous_luxury = basic.luxury_start
            budget_end, luxury_start = update_basic_price_points(basic)

            if budget_end is not None and luxury_start is not None:
                self.stdout.write(basic.name.upper())
                self.stdout.write('Budget End: $%.02f => $%.02f' % (previous_budget, budget_end))
                self.stdout.write('Luxury Start: $%.02f => $%.02f\n\n' % (previous_luxury, luxury_start))
            else:
                self.stdout.write('%s [!]' % basic.name.upper())
                self.stdout.write('No pricing information available\n\n')
