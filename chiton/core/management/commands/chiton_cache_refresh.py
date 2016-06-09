from django.core.cache import cache
from django.core.management.base import BaseCommand

from chiton.core.queries import prime_cached_queries


class Command(BaseCommand):
    help = 'Refresh all cached data'

    def handle(self, *arg, **options):
        cache.clear()
        self.stdout.write('Cache cleared')

        prime_cached_queries()
        self.stdout.write('Cached queries primed')
