from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManager


class GarmentManager(models.Manager):
    """A custom manager for garments."""

    def get_by_natural_key(self, slug, line_slug):
        return self.get(slug=slug, line__slug=line_slug)


class Garment(models.Model):
    """An article of clothing."""

    objects = GarmentManager()

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    line = models.ForeignKey('Line', on_delete=models.CASCADE, verbose_name=_('line'))
    category = models.ForeignKey('GarmentCategory', on_delete=models.CASCADE, verbose_name=_('category'))

    class Meta:
        verbose_name = _('garment')
        verbose_name_plural = _('garments')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug, self.line.slug)


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


class LineManager(models.Manager):
    """A custom manager for clothing lines."""

    def get_by_natural_key(self, slug, brand_slug):
        return self.get(slug=slug, brand__slug=brand_slug)


class Line(models.Model):
    """A line of clothing offered by a brand."""

    objects = LineManager()

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name=_('brand'))

    class Meta:
        verbose_name = _('line')
        verbose_name_plural = _('lines')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug, self.brand.slug)


class GarmentCategoryManager(TreeManager):
    """A custom manager for garment categories."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class GarmentCategory(MPTTModel):
    """The category in which a garment belongs, such as shirt or pants."""

    objects = GarmentCategoryManager()

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
