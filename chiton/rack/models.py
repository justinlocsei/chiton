from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet.models import Garment


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
    garment = models.ForeignKey(Garment, on_delete=models.CASCADE, verbose_name=_('garment'))
    last_modified = models.DateTimeField(verbose_name=_('last modified'), auto_now=True, db_index=True)

    class Meta:
        verbose_name = _('affiliate item')
        verbose_name_plural = _('affiliate items')

    def __str__(self):
        return self.name
