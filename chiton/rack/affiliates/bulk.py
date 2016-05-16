from io import StringIO
from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue
import traceback

from chiton.rack.affiliates.data import update_affiliate_item_details, update_affiliate_item_metadata


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
    queue = Queue()

    def refresh_item(item):
        label = '%s: %s' % (item.network.name, item.name)
        try:
            item_updater(item)
        except Exception:
            error_buffer = StringIO()
            traceback.print_exc(file=error_buffer)
            queue.put({
                'details': error_buffer.getvalue().strip(),
                'label': label,
                'is_error': True
            })
        else:
            queue.put({
                'label': label,
                'is_error': False
            })

    pool = ThreadPool(workers)
    pool.map_async(refresh_item, items)
    pool.close()

    return queue
