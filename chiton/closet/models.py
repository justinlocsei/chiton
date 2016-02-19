from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Garment(models.Model):
    """An article of clothing."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)

    class Meta:
        verbose_name = _('garment')
        verbose_name_plural = _('garments')

    def __str__(self):
        return self.name


class Brand(models.Model):
    """A brand of clothing."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    url = models.URLField(max_length=255, verbose_name=_('URL'), null=True, blank=True)

    class Meta:
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    def __str__(self):
        return self.name


class Line(models.Model):
    """A line of clothing offered by a brand."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name=_('brand'))

    class Meta:
        verbose_name = _('line')
        verbose_name_plural = _('lines')

    def __str__(self):
        return self.name


class GarmentCategory(MPTTModel):
    """The category in which a garment belongs, such as shirt or pants."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    parent = TreeForeignKey('self', null=True, blank=True)

    class Meta:
        verbose_name = _('garment category')
        verbose_name_plural = _('garment categories')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class GarmentOption(models.Model):
    """An option for a garment, such as its fit or sleeve length."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)

    class Meta:
        verbose_name = _('garment option')
        verbose_name_plural = _('garment options')

    def __str__(self):
        return self.name
