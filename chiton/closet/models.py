from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _


class GarmentManager(models.Manager):
    """A custom manager for garments."""

    def get_by_natural_key(self, slug, brand_slug):
        return self.get(slug=slug, brand__slug=brand_slug)


class Garment(models.Model):
    """An article of clothing."""

    objects = GarmentManager()

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, verbose_name=_('brand'))

    class Meta:
        verbose_name = _('garment')
        verbose_name_plural = _('garments')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug, self.brand.slug)


class BrandManager(models.Manager):
    """A custom manager for brands."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Brand(models.Model):
    """A brand of clothing."""

    objects = BrandManager()

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    url = models.URLField(max_length=255, verbose_name=_('URL'), null=True, blank=True)

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)



class GarmentOption(models.Model):
    """An option for a garment, such as its fit or sleeve length."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)

    class Meta:
        verbose_name = _('garment option')
        verbose_name_plural = _('garment options')

    def __str__(self):
        return self.name
