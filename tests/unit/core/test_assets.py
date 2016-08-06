import subprocess

import mock

from chiton.core.assets import sync_media_with_cdn


class TestSyncMediaWithCdn:

    def test_shell_out(self, settings):
        """It calls the external sync script with the media directory and CDN asset directory."""
        settings.CDN_SYNC_SCRIPT = 'cdn-sync'
        settings.MEDIA_ROOT = '/tmp/media'
        settings.CDN_ASSET_DIR = 'assets'

        with mock.patch('chiton.core.assets.Popen') as popen:
            popen.return_value = subprocess.Popen(['true'])
            sync_media_with_cdn()

            popen.assert_called_with(['cdn-sync', '/tmp/media', 'assets'])

    def test_shell_out_blocking(self):
        """It blocks until the shell call terminates."""
        with mock.patch('chiton.core.assets.Popen') as popen:
            popen.return_value = subprocess.Popen(['true'])

            assert sync_media_with_cdn()

    def test_shell_out_error(self):
        """It returns false when the shell call fails."""
        with mock.patch('chiton.core.assets.Popen') as popen:
            popen.return_value = subprocess.Popen(['false'])

            assert not sync_media_with_cdn()
