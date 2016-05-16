from io import StringIO
from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue
import traceback

from chiton.rack.affiliates.data import update_affiliate_item_details


def bulk_update_affiliate_item_details(items, full=False, workers=2):
    """Refresh a batch of affiliate items.

    Args:
        items (django.db.models.query.QuerySet): A queryset of affiliate items

    Keyword Args:
        full (bool): Whether to perform a full refresh
        workers (int): The number of workers to use to process the items

    Returns:
        queue.Queue: A queue that will contain all processed affiliate items
    """
    items = items.select_related('garment__basic', 'image', 'thumbnail', 'network')

    pool = ThreadPool(workers)
    queue = Queue()

    def refresh_item(item):
        label = '%s: %s' % (item.network.name, item.name)
        try:
            item = update_affiliate_item_details(item, full=full)
            queue.put({
                'label': label,
                'is_error': False
            })
        except Exception:
            error_buffer = StringIO()
            traceback.print_exc(file=error_buffer)
            queue.put({
                'details': error_buffer.getvalue().strip(),
                'label': label,
                'is_error': True
            })

    pool.map_async(refresh_item, items)
    pool.close()

    return queue
