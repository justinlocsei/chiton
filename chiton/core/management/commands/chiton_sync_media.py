from django.core.management.base import BaseCommand
from django.conf import settings

from chiton.core.assets import sync_media_with_cdn


class Command(BaseCommand):
    help = 'Sync media with the CDN'

    def handle(self, *arg, **options):
        if settings.CDN_ENABLED:
            self.stdout.write('Syncing media with the CDN')
            sync_media_with_cdn()
        else:
            self.stdout.write('CDN is not used, skipping sync')
