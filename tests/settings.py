import logging

from chiton.settings import *

# Use a test-specific local-memory cache
CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'chiton_tests'
}

# Disable logging
logging.disable(logging.CRITICAL)
