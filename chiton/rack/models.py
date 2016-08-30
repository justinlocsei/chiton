import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet.models import Garment, StandardSize
from chiton.closet.model_fields import PriceField


class AffiliateNetworkManager(models.Manager):
    """A custom manager for affiliates."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class AffiliateNetwork(models.Model):
    """An affiliate network."""

    objects = AffiliateNetworkManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    slug = models.SlugField(max_length=255, verbose_name=_('slug'), unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('affiliate network')
        verbose_name_plural = _('affiliate networks')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class AffiliateItem(models.Model):
    """An item provided by an affiliate network."""

    network = models.ForeignKey(AffiliateNetwork, on_delete=models.CASCADE, verbose_name=_('affiliate network'))
    url = models.TextField(verbose_name=_('URL'))
    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    guid = models.CharField(max_length=255, verbose_name=_('GUID'))
    garment = models.ForeignKey(Garment, on_delete=models.CASCADE, verbose_name=_('garment'), related_name='affiliate_items')
    last_modified = models.DateTimeField(verbose_name=_('last modified'), auto_now=True, db_index=True)
    price = PriceField(verbose_name=_('price'), null=True, blank=True, db_index=True)
    has_detailed_stock = models.BooleanField(verbose_name=('has detailed stock'), default=False)
    retailer = models.CharField(max_length=255, verbose_name=_('retailer'), db_index=True)
    affiliate_url = models.TextField(verbose_name=_('affiliate URL'))

    class Meta:
        unique_together = ('guid', 'network')
        verbose_name = _('affiliate item')
        verbose_name_plural = _('affiliate items')

    def __str__(self):
        return self.name


class StockRecord(models.Model):
    """A record of an item's availability."""

    item = models.ForeignKey(AffiliateItem, on_delete=models.CASCADE, verbose_name=_('affiliate item'), related_name='stock_records')
    size = models.ForeignKey(StandardSize, on_delete=models.CASCADE, verbose_name=_('size'))
    is_available = models.BooleanField(verbose_name=_('is available'), default=False)

    class Meta:
        verbose_name = _('stock record')
        verbose_name_plural = _('stock records')


def _upload_path_for_item_image(item_image, filename):
    """Upload item images to subdirectories based on their item."""
    return os.path.join('products', str(item_image.item.pk), os.path.basename(filename))


class ItemImage(models.Model):
    """An image for an item."""

    item = models.ForeignKey(AffiliateItem, on_delete=models.CASCADE, verbose_name=_('affiliate item'), related_name='images')
    file = models.ImageField(upload_to=_upload_path_for_item_image, verbose_name=_('file'), height_field='height', width_field='width')
    height = models.PositiveIntegerField(verbose_name=_('height'))
    width = models.PositiveIntegerField(verbose_name=_('width'))
    source_url = models.URLField(verbose_name=_('source URL'))

    class Meta:
        verbose_name = _('item image')
        verbose_name_plural = _('item images')

    def __str__(self):
        return '%dx%d' % (self.width, self.height)
