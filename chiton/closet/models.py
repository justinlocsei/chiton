from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet import data
from chiton.closet.model_fields import EmphasisField
from chiton.core.validators import validate_loose_range
from chiton.runway.models import Basic, Formality, Style


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
    basic = models.ForeignKey(Basic, on_delete=models.CASCADE, verbose_name=_('basic type'))
    shoulder_emphasis = EmphasisField(verbose_name=_('shoulder emphasis'))
    waist_emphasis = EmphasisField(verbose_name=_('waist emphasis'))
    hip_emphasis = EmphasisField(verbose_name=_('hip emphasis'))
    sleeve_length = models.CharField(max_length=15, choices=data.SLEEVE_LENGTH_CHOICES, verbose_name=_('sleeve length'), null=True, blank=True)
    bottom_length = models.CharField(max_length=15, choices=data.BOTTOM_LENGTH_CHOICES, verbose_name=_('bottom length'), null=True, blank=True)
    pant_rise = models.CharField(max_length=15, choices=data.PANT_RISE_CHOICES, verbose_name=_('pant rise'), null=True, blank=True)
    description = models.TextField(verbose_name=_('description'), help_text=_('A public description'), null=True, blank=True)
    notes = models.TextField(verbose_name=_('notes'), help_text=_('Internal information'), null=True, blank=True)
    is_busty = models.NullBooleanField(verbose_name=_('is for busty women'))
    is_plus_sized = models.BooleanField(verbose_name=_('is for plus-sized women'), default=False)
    is_featured = models.BooleanField(verbose_name=_('is featured'), default=False)
    care = models.CharField(max_length=25, choices=data.CARE_CHOICES, verbose_name=_('care instructions'), null=True, blank=True)
    styles = models.ManyToManyField(Style, verbose_name=_('styles'))
    formalities = models.ManyToManyField(Formality, verbose_name=_('levels of formality'))
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('updated at'), auto_now=True)

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


class ColorManager(models.Manager):
    """A custom manager for colors."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Color(models.Model):
    """A canonical color for an item."""

    objects = ColorManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('color')
        verbose_name_plural = _('colors')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


def _slug_for_size(size):
    """Create the slug for a Size model instance."""
    parts = [size.base]

    if size.is_tall:
        parts.append('tall')
    elif size.is_petite:
        parts.append('petite')

    return '-'.join(parts)


class SizeManager(models.Manager):
    """A custom manager for sizes."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Size(models.Model):
    """A canonical size for an item."""

    objects = SizeManager()

    base = models.CharField(max_length=15, choices=data.SIZE_CHOICES, verbose_name=_('base size'))
    slug = AutoSlugField(max_length=255, populate_from=_slug_for_size, verbose_name=_('slug'), unique=True)
    size_lower = models.PositiveSmallIntegerField(verbose_name=_('lower numeric size'))
    size_upper = models.PositiveSmallIntegerField(verbose_name=_('upper numeric size'))
    is_petite = models.BooleanField(verbose_name=_('is petite'), default=False)
    is_tall = models.BooleanField(verbose_name=_('is tall'), default=False)
    position = models.PositiveSmallIntegerField(verbose_name=_('position'), default=0)

    class Meta:
        ordering = ('position',)
        unique_together = ('size_lower', 'size_upper', 'is_tall', 'is_petite')
        verbose_name = _('size')
        verbose_name_plural = _('sizes')

    def __str__(self):
        return self.full_name

    def natural_key(self):
        return (self.slug,)

    def clean(self):
        """Ensure correct ordering of the size range and unique variants."""
        validate_loose_range(self.size_lower, self.size_upper)

        if self.is_tall and self.is_petite:
            raise ValidationError(_('A size cannot be both tall and petite'))

    @property
    def full_name(self):
        """Show the full name of the size, with its possible variant and range.

        Returns:
            str: The full name for the size
        """
        ranges = sorted(list(set([self.size_lower, self.size_upper])))
        range_display = '-'.join([str(r) for r in ranges])
        base = '%s (%s)' % (self.get_base_display(), range_display)

        if self.is_tall:
            return _('Tall %(size)s') % {'size': base}
        elif self.is_petite:
            return _('Petite %(size)s') % {'size': base}
        else:
            return base
