from subprocess import Popen

from django.conf import settings


def sync_media_with_cdn():
    """Sync all local media with the CDN.

    Returns:
        bool: Whether the sync was successful
    """
    sync = Popen([
        settings.CDN_SYNC_SCRIPT,
        settings.MEDIA_ROOT,
        settings.CDN_ASSET_DIR
    ])
    sync.wait()

    return sync.returncode == 0
