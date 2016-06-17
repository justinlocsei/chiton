from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet import data
from chiton.closet.model_fields import EmphasisField
from chiton.core.queries import cache_query
from chiton.core.validators import validate_range
from chiton.runway.models import Basic, Formality, Style


class GarmentManager(models.Manager):
    """A custom manager for garments."""

    def get_by_natural_key(self, slug, brand_slug):
        return self.get(slug=slug, brand__slug=brand_slug)


class Garment(models.Model):
    """An article of clothing."""

    SIZE_FIELDS = ('is_petite_sized', 'is_plus_sized', 'is_regular_sized', 'is_tall_sized')

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
    is_regular_sized = models.BooleanField(verbose_name=_('is available in regular sizes'), default=True)
    is_plus_sized = models.BooleanField(verbose_name=_('is available in plus sizes'), default=False)
    is_tall_sized = models.BooleanField(verbose_name=_('is available in tall sizes'), default=False)
    is_petite_sized = models.BooleanField(verbose_name=_('is available in petite sizes'), default=False)
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

    def clean(self):
        """Ensure that at least one size is marked as available."""
        if not any([getattr(self, s) for s in self.SIZE_FIELDS]):
            raise ValidationError(_('At least one size-availability field must be true'))


class BrandManager(models.Manager):
    """A custom manager for brands."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Brand(models.Model):
    """A brand of clothing."""

    objects = BrandManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    age_lower = models.PositiveSmallIntegerField(verbose_name=_('lower target age'))
    age_upper = models.PositiveSmallIntegerField(verbose_name=_('upper target age'))

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
        validate_range(self.age_lower, self.age_upper, loose=True)


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


class CanonicalSizeManager(models.Manager):
    """A custom manager for canonical sizes."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class CanonicalSize(models.Model):
    """A canonical size for an item."""

    objects = CanonicalSizeManager()

    name = models.CharField(max_length=25, choices=data.SIZE_CHOICES, verbose_name=_('name'), unique=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    range_lower = models.PositiveSmallIntegerField(verbose_name=_('lower numeric size'))
    range_upper = models.PositiveSmallIntegerField(verbose_name=_('upper numeric size'))
    position = models.PositiveSmallIntegerField(verbose_name=_('position'), default=0)

    class Meta:
        ordering = ('position',)
        unique_together = ('name', 'range_lower', 'range_upper')
        verbose_name = _('canonical size')
        verbose_name_plural = _('canonical sizes')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)

    def clean(self):
        """Ensure correct ordering of the size range."""
        validate_range(self.range_lower, self.range_upper)


def _make_slug_for_standard_size(size):
    """Make a slug for a given size.

    Args:
        chiton.closet.models.StandardSize: A standard size model

    Returns:
        str: The slug for the size
    """
    parts = [size.canonical.slug]

    if size.is_tall:
        parts.append('tall')
    elif size.is_petite:
        parts.append('petite')
    elif size.is_plus_sized:
        parts.append('plus')

    return '-'.join(parts)


class StandardSizeManager(models.Manager):
    """A custom manager for standard sizes."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_slugs(self):
        """Return a list of all size slugs.

        Returns:
            list[str]: All size slugs
        """
        return _get_standard_size_slugs()


class StandardSize(models.Model):
    """A standard size for an item."""

    VARIANT_FIELDS = ('is_regular', 'is_tall', 'is_petite', 'is_plus_sized')

    objects = StandardSizeManager()

    canonical = models.ForeignKey(CanonicalSize, on_delete=models.CASCADE, verbose_name=_('canonical size'))
    slug = AutoSlugField(max_length=255, populate_from=_make_slug_for_standard_size, verbose_name=_('slug'), unique=True)
    is_regular = models.BooleanField(verbose_name=_('regular'), default=True)
    is_tall = models.BooleanField(verbose_name=_('tall'), default=False)
    is_petite = models.BooleanField(verbose_name=_('petite'), default=False)
    is_plus_sized = models.BooleanField(verbose_name=_('plus-sized'), default=False)
    position = models.PositiveSmallIntegerField(verbose_name=_('position'), default=0)

    class Meta:
        ordering = ('position',)
        unique_together = ('canonical', 'is_tall', 'is_petite', 'is_regular', 'is_plus_sized')
        verbose_name = _('standard size')
        verbose_name_plural = _('standard sizes')

    def __str__(self):
        return self.display_name

    def natural_key(self):
        return (self.slug,)

    def clean(self):
        """Ensure that only one variant is selected."""
        variants = [getattr(self, field) for field in self.VARIANT_FIELDS]
        variant_count = len([v for v in variants if v])

        if not variant_count:
            raise ValidationError('A variant type must be selected')
        elif variant_count > 1:
            raise ValidationError('Only one variant type may be selected')

    @property
    def display_name(self):
        """Get the formatted name of the size for display.

        Returns:
            str: The formatted size name
        """
        canonical = self.canonical
        names = []

        if self.is_tall:
            names.append('Tall')
        elif self.is_petite:
            names.append('Petite')
        elif self.is_plus_sized:
            names.append('Plus')

        names.append(canonical.name)

        lower_range = canonical.range_lower
        upper_range = canonical.range_upper
        if lower_range != upper_range:
            numbers = [lower_range, upper_range]
        else:
            numbers = [lower_range]

        return '%s (%s)' % (
            ' '.join(names),
            '-'.join([str(n) for n in numbers])
        )


@cache_query(CanonicalSize, StandardSize)
def _get_standard_size_slugs():
    """Return all StandardSize slugs."""
    return list(StandardSize.objects.all().order_by('slug').values_list('slug', flat=True))
