from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet import data
from chiton.closet.model_fields import EmphasisField
from chiton.core.validators import validate_loose_range


class GarmentManager(models.Manager):
    """A custom manager for garments."""

    def get_by_natural_key(self, slug, brand_slug):
        return self.get(slug=slug, brand__slug=brand_slug)


class Garment(models.Model):
    """An article of clothing."""

    objects = GarmentManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE, verbose_name=_('brand'))
    shoulder_emphasis = EmphasisField(verbose_name=_('shoulder emphasis'))
    waist_emphasis = EmphasisField(verbose_name=_('waist emphasis'))
    hip_emphasis = EmphasisField(verbose_name=_('hip emphasis'))
    sleeve_length = models.CharField(max_length=15, choices=data.SLEEVE_LENGTH_CHOICES, verbose_name=_('sleeve length'), null=True)
    bottom_length = models.CharField(max_length=15, choices=data.BOTTOM_LENGTH_CHOICES, verbose_name=_('bottom length'), null=True)
    description = models.TextField(verbose_name=_('description'), help_text=_('A public description'), null=True, blank=True)
    notes = models.TextField(verbose_name=_('notes'), help_text=_('Internal information'), null=True, blank=True)

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

    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    age_lower = models.PositiveSmallIntegerField(verbose_name=_('lower target age'), null=True, blank=True)
    age_upper = models.PositiveSmallIntegerField(verbose_name=_('upper target age'), null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('brand')
        verbose_name_plural = _('brands')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

    def clean(self):
        """Ensure correct ordering of the age range."""
        validate_loose_range(self.age_lower, self.age_upper)


class GarmentOption(models.Model):
    """An option for a garment, such as its fit or sleeve length."""

    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)

    class Meta:
        verbose_name = _('garment option')
        verbose_name_plural = _('garment options')

    def __str__(self):
        return self.name
