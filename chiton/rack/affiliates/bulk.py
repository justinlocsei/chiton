from io import StringIO
from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue
import random
from time import sleep
from traceback import print_exc

from chiton.rack.affiliates.data import update_affiliate_item_details, update_affiliate_item_metadata
from chiton.rack.affiliates.exceptions import ThrottlingError


# The maximum number of retries in response to API throttling
MAX_API_RETRIES = 10

# The initial timeout when handling a throttled API request, in seconds
API_TIMEOUT = 1.5

# The maximum API sleep time, in seconds
MAX_API_SLEEP = 15


def bulk_update_affiliate_item_metadata(items, workers=2):
    """Refresh the metadata for a batch of affiliate items.

    Args:
        items (django.db.models.query.QuerySet): A queryset of affiliate items

    Keyword Args:
        workers (int): The number of workers to use to process the items

    Returns:
        queue.Queue: A queue that will contain all processed affiliate items
    """
    items = items.select_related('network')
    return _bulk_update_items(items, update_affiliate_item_metadata, workers)


def bulk_update_affiliate_item_details(items, workers=2):
    """Refresh the details for a batch of affiliate items.

    Args:
        items (django.db.models.query.QuerySet): A queryset of affiliate items

    Keyword Args:
        workers (int): The number of workers to use to process the items

    Returns:
        queue.Queue: A queue that will contain all processed affiliate items
    """
    items = items.select_related('garment__basic', 'image', 'thumbnail', 'network')
    return _bulk_update_items(items, update_affiliate_item_details, workers)


def _bulk_update_items(items, item_updater, workers):
    """Create a function that can be used for bulk updates of an item.

    Args:
        items (django.db.models.query.QuerySet): A queryset of affiliate items
        item_updater (function): A function to update a single item
        workers (int): The number of workers to use

    Returns:
        queue.Queue: A queue that will contain information on processed items
    """
    retry_range = range(1, MAX_API_RETRIES + 5)
    queue = Queue()

    def refresh_item(item):
        label = '%s: %s' % (item.network.name, item.name)

        for retry_index in retry_range:
            try:
                item_updater(item)

            # If we receive a throttling error from the API, and we have yet to
            # exceed the maximum retries, randomly calculate a delay using an
            # exponential backoff algorithm.  If the maximum retries have been
            # exceeded, add an error message to the work queue.
            except ThrottlingError:
                if retry_index < MAX_API_RETRIES:
                    delay = random.uniform(1, min(MAX_API_SLEEP, API_TIMEOUT * 2 ** retry_index))
                    sleep(delay)
                else:
                    return queue.put({
                        'details': 'Exceeded max throttling retries of %d' % MAX_API_RETRIES,
                        'label': label,
                        'is_error': True
                    })

            # If the API call resuled in an error of any kind, capture the
            # error's traceback and add it as the detail message to the queue
            except Exception:
                error_buffer = StringIO()
                print_exc(file=error_buffer)
                return queue.put({
                    'details': error_buffer.getvalue().strip(),
                    'label': label,
                    'is_error': True
                })

            # If the API call succeeded, add a success message to the queue
            else:
                return queue.put({
                    'label': label,
                    'is_error': False
                })

    pool = ThreadPool(workers)
    pool.map_async(refresh_item, items)
    pool.close()

    return queue
