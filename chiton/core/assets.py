import subprocess

from django.conf import settings


def sync_media_with_cdn():
    """Sync all local media with the CDN."""
    sync = subprocess.Popen([
        settings.CDN_SYNC_SCRIPT,
        settings.MEDIA_ROOT,
        settings.CDN_ASSET_DIR
    ])
    sync.wait()
