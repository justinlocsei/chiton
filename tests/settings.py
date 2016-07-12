import logging
import os
import shutil
import tempfile

from chiton.settings import *

# Use a temporary directory for media files
MEDIA_ROOT = os.path.join(tempfile.gettempdir(), 'chiton-test')
if os.path.isdir(MEDIA_ROOT):
    shutil.rmtree(MEDIA_ROOT)
os.mkdir(MEDIA_ROOT)

# Use a test-specific local-memory cache
CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'chiton_tests'
}

# Disable logging
logging.disable(logging.CRITICAL)
