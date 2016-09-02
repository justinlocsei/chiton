import os

from django.core.files.base import ContentFile
import requests

from chiton.closet.models import StandardSize
from chiton.rack.affiliates import create_affiliate
from chiton.rack.models import ItemImage, StockRecord


def update_affiliate_item_metadata(item):
    """Update the metadata for an affiliate item from its network's API.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item

    Returns:
        chiton.rack.models.AffiliateItem: The updated affiliate item

    Raises:
        chiton.rack.exceptions.LookupError: If the item's information cannot be updated
    """
    affiliate = create_affiliate(slug=item.network.slug)

    overview = affiliate.request_overview(item.url)
    item.guid = overview['guid']
    item.name = overview['name']

    item.save()
    return item


def update_affiliate_item_details(item):
    """Update the details for an affiliate item from its network's API.

    This sends a details query to the API of the item's affiliate network, and
    updates the item record with the response data.  If the `full` keyword arg
    is true, this will first re-fetch the item's GUID from its URL, and then
    issue the details query.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item

    Returns:
        chiton.rack.models.AffiliateItem: The updated affiliate item

    Raises:
        chiton.rack.exceptions.LookupError: If the item's information cannot be updated
    """
    affiliate = create_affiliate(slug=item.network.slug)
    basic = item.garment.basic

    # Place the primary color at the head of the colors list for fetching
    # details, followed by the secondary colors
    color_names = []
    primary_color_name = getattr(basic.primary_color, 'name', None)
    if primary_color_name:
        color_names.append(primary_color_name)
    color_names += basic.secondary_colors.values_list('name', flat=True)

    details = affiliate.request_details(item.guid, colors=color_names)

    item.name = details['name']
    item.price = details['price']
    item.retailer = details['retailer']
    item.affiliate_url = details['url']
    _update_item_images(item, details['images'])
    _update_stock_records(item, details['availability'])

    item.save()
    return item


def _update_item_images(item, image_urls):
    """Update the image associated with an affiliate item.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item
        image_urls (list[str]): The URLs of all item images
    """
    all_images = [image for image in item.images.all()]
    missing_images = [image for image in all_images if not os.path.isfile(image.file.path)]
    existing_images = [image for image in all_images if image not in missing_images]

    for image_url in image_urls:
        existing_matches = [ei for ei in existing_images if ei.source_url == image_url]
        if not existing_matches:
            item_image = ItemImage(item=item, source_url=image_url)

            image_path = os.path.join(str(item.pk), image_url.split('/')[-1])
            item_image.file.save(image_path, _download_image(image_url))

            item_image.save()

    prune_images = [image for image in existing_images if image.source_url not in image_urls]
    for image in prune_images + missing_images:
        image.delete()


def _download_image(url):
    """Download an item image.

    This saves to the image to the media directory, then returns a file
    reference to it that can be associated with an ItemImage model.

    Args:
        url (str): The URL of the image

    Returns:
        django.core.files.ContentFile: The image's contents
    """
    request = requests.get(url)
    return ContentFile(request.content)


def _update_stock_records(item, availability):
    """Update an item's stock records.

    This looks at the sizes of the given stock records and maps them to known
    canonical sizes.  If availability records are present, a stock record is
    created that marks the item as in-stock for the source record's size.  If no
    record is present for a size, an out-of-stock record is created instead.

    Availability can also be indicated as a boolean value indicating that an
    item is globally available or unavailable.  A true value will mark the item
    as in-stock, while a false one will cause it to be marked as out-of-stock.

    Any reported availability is used to modify the base availability determined
    by looking at the manually entered size ranges in which a garment should be
    available.  For example, if an affiliate item is marked as being available
    in regular sizes, if no availability information is returned, an in-stock
    stock record will be created for every regular size.  If availability
    information is returned, any reported availability not in a regular size
    will be ignored.

    Args:
        item (chiton.rack.models.AffiliateItem): An affiliate item
        availability (bool,list): Information on the item's availability
    """
    all_sizes = StandardSize.objects.all()
    existing_records = item.stock_records.all().select_related('size__canonical')
    has_details = False

    # Default to marking all known sizes as out of stock
    available_sizes = {}
    for size in all_sizes:
        available_sizes[size] = False

    # If global or specific availability was provided, mark in-stock items
    if availability:
        garment = item.garment
        if isinstance(availability, bool):
            has_records = False
        else:
            has_records = True
            has_details = len(availability) > 0

        # Get a subset of sizes that map to the size types of the garments by
        # comparing the type signatures
        garment_signature = {
            'is_regular': garment.is_regular_sized,
            'is_petite': garment.is_petite_sized,
            'is_tall': garment.is_tall_sized,
            'is_plus_sized': garment.is_plus_sized
        }
        type_sizes = []
        for size in all_sizes:
            for availability_field, garment_value in garment_signature.items():
                if garment_value and getattr(size, availability_field):
                    type_sizes.append(size)
                    break

        # Map reported availability to unambiguous standard sizes
        reported_sizes = set()
        if has_records:
            for record in availability:
                matches = [
                    size for size in type_sizes
                    if record['is_regular'] == size.is_regular
                    and record['is_petite'] == size.is_petite
                    and record['is_tall'] == size.is_tall
                    and record['is_plus_sized'] == size.is_plus_sized
                    and size.canonical.range_lower <= record['size'] <= size.canonical.range_upper
                ]
                if len(matches) == 1:
                    reported_sizes.add(matches[0])

        # Unmark the has-records flag if none of the reported sizes match a size
        # type selected by the garment
        if has_records and not reported_sizes:
            has_records = False

        # Update the availability map with the computed values
        for size in type_sizes:
            if has_records:
                available_sizes[size] = size in reported_sizes
            else:
                available_sizes[size] = True

    # Create a new stock record for the item or update an existing record
    for size in all_sizes:
        current_record = None
        for existing_record in existing_records:
            if existing_record.size == size:
                current_record = existing_record
                break

        if current_record:
            current_record.is_available = available_sizes[size]
            current_record.save()
        else:
            StockRecord.objects.create(
                item=item,
                size=size,
                is_available=available_sizes[size]
            )

    # If the item's stock-detail state has changed, update it
    if has_details is not item.has_detailed_stock:
        item.has_detailed_stock = has_details
        item.save()
