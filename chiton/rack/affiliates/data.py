from multiprocessing.dummy import Pool as ThreadPool
from queue import Queue

from chiton.closet.models import Size
from chiton.rack.affiliates import create_affiliate
from chiton.rack.models import ProductImage, StockRecord


def refresh_affiliate_items(items, full=False, workers=2):
    """Refresh a batch of affiliate items.

    Args:
        items (django.db.models.query.QuerySet): A queryset of affiliate items

    Keyword Args:
        full (bool): Whether to perform a full refresh
        workers (int): The number of workers to use to process the items

    Returns:
        queue.Queue: A queue that will contain all processed affiliate items
    """
    items = items.select_related('garment__basic', 'image', 'thumbnail')

    pool = ThreadPool(workers)
    queue = Queue()

    def refresh_item(item):
        queue.put({'item_name': item.name})

    pool.map_async(refresh_item, items)
    pool.close()

    return queue


def refresh_affiliate_item(item, full=False):
    """Refresh the data for an affiliate item based on an API query.

    This sends a details query to the API of the item's affiliate network, and
    updates the item record with the response data.  If the `full` keyword arg
    is true, this will first re-fetch the item's GUID from its URL, and then
    issue the details query.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item

    Keyword Args:
        full (bool): Whether to perform a full refresh

    Returns:
        chiton.rack.models.AffiliateItem: The updated affiliate item

    Raises:
        chiton.rack.exceptions.LookupError: If the item's information cannot be updated
    """
    affiliate = create_affiliate(slug=item.network.slug)
    basic = item.garment.basic

    if full:
        overview = affiliate.request_overview(item.url)
        item.guid = overview.guid
        item.name = overview.name

    # Place the primary color at the head of the colors list for fetching
    # details, followed by the secondary colors
    color_names = []
    primary_color_name = getattr(basic.primary_color, 'name', None)
    if primary_color_name:
        color_names.append(primary_color_name)
    color_names += basic.secondary_colors.values_list('name', flat=True)

    details = affiliate.request_details(item.guid, colors=color_names)

    item.price = details.price
    _update_item_image(item, 'image', details.image)
    _update_item_image(item, 'thumbnail', details.thumbnail)
    _update_stock_records(item, details.availability)

    item.save()

    return item


def _update_item_image(item, image_field, data):
    """Update the image associated with an affiliate item.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item
        image_field (str): The name of the image field on the item
        data (dict): The API response describing the image
    """
    image = getattr(item, image_field)

    if image:
        image.height = data.height
        image.width = data.width
        image.url = data.url
        image.save()
    else:
        image = ProductImage.objects.create(
            height=data.height,
            width=data.width,
            url=data.url
        )
        setattr(item, image_field, image)


def _update_stock_records(item, records):
    """Update an item's stock records.

    This looks at the sizes of the given stock records and maps them to known
    canonical sizes.  If an availability record is present, a stock record is
    created that marks the item as in-stock.  If no record is present, an
    out-of-stock record is created instead.

    If no availability information at all is provided, a stock record showing
    the item as in-stock is created for every known size.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item
        records (list): Possible ItemAvailability instances for the item
    """
    all_sizes = Size.objects.all()
    existing_records = item.stock_records.all().select_related('size')

    has_info = records is not None
    record_sizes = [r.size for r in records or []]

    # Build a map between Size instances and availability, as indicated by
    # occurrences of known sizes in the given availability records
    availability = {}
    for size in all_sizes:
        if has_info:
            is_available = size.full_name in record_sizes
        else:
            is_available = True
        availability[size] = is_available

    for size in all_sizes:
        current_record = None
        for existing_record in existing_records:
            if existing_record.size == size:
                current_record = existing_record
                break

        if current_record:
            current_record.is_available = availability[size]
            current_record.save()
        else:
            StockRecord.objects.create(
                item=item,
                size=size,
                is_available=availability[size]
            )
