from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet.model_fields import PriceField
from chiton.core.queries import cache_query
from chiton.runway import data


class BasicManager(models.Manager):
    """A custom manager for basics."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Basic(models.Model):
    """A basic role fulfilled by a garment."""

    objects = BasicManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), unique=True)
    plural_name = models.CharField(max_length=255, verbose_name=_('plural name'))
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    category = models.ForeignKey('Category', verbose_name=_('category'), on_delete=models.SET_NULL, null=True, blank=True)
    formalities = models.ManyToManyField('Formality', verbose_name=_('levels of formality'), through='Propriety')
    primary_color = models.ForeignKey('chiton_closet.Color', on_delete=models.SET_NULL, verbose_name=_('primary color'), related_name='primary_for', null=True, blank=True)
    secondary_colors = models.ManyToManyField('chiton_closet.Color', verbose_name=_('secondary colors'), related_name='secondary_for', blank=True)
    budget_end = PriceField(verbose_name=_('budget end price'), default=0)
    luxury_start = PriceField(verbose_name=_('luxury start price'), default=0)

    class Meta:
        ordering = ('name',)
        verbose_name = _('basic')
        verbose_name_plural = _('basics')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class CategoryManager(models.Manager):
    """A custom manager for categories."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Category(models.Model):
    """A category for a basic."""

    objects = CategoryManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), unique=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    position = models.PositiveSmallIntegerField(verbose_name=_('position'), default=0)

    class Meta:
        ordering = ('position',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class ProperietyManager(models.Manager):
    """A custom manager for proprieties."""

    def get_by_natural_key(self, basic, formality, importance):
        return self.get(basic__slug=basic, formality__slug=formality, importance=importance)

    def for_export(self):
        """Return a set of all proprieties sorted deterministically for export."""
        return self.all().order_by('basic__name', 'formality__slug', 'importance')


class Propriety(models.Model):
    """A relation between a basic and a level of formality."""

    objects = ProperietyManager()

    basic = models.ForeignKey(Basic, on_delete=models.CASCADE, verbose_name=_('basic'))
    formality = models.ForeignKey('Formality', on_delete=models.CASCADE, verbose_name=_('level of formality'))
    importance = models.CharField(max_length=25, choices=data.PROPRIETY_IMPORTANCE_CHOICES, verbose_name=_('importance'))

    class Meta:
        verbose_name = _('propriety')
        verbose_name_plural = _('proprieties')

    def natural_key(self):
        return (self.basic.slug, self.formality.slug, self.importance)


class StyleManager(models.Manager):
    """A custom manager for styles."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_slugs(self):
        """Return a list of all style slugs.

        Returns:
            list[str]: All style slugs
        """
        return _get_style_slugs()


class Style(models.Model):
    """A style conveyed by a garment."""

    objects = StyleManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), unique=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('style')
        verbose_name_plural = _('styles')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class FormalityManager(models.Manager):
    """A custom manager for formalities."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

    def get_slugs(self):
        """Return a list of all formality slugs.

        Returns:
            list[str]: All formality slugs
        """
        return _get_formality_slugs()


class Formality(models.Model):
    """A level of formality."""

    objects = FormalityManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), db_index=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    position = models.PositiveSmallIntegerField(verbose_name=_('position'), default=0)

    class Meta:
        ordering = ('position',)
        verbose_name = _('level of formality')
        verbose_name_plural = _('levels of formality')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


@cache_query(Formality)
def _get_formality_slugs():
    """Return all Formality slugs."""
    return list(Formality.objects.all().order_by('slug').values_list('slug', flat=True))


@cache_query(Style)
def _get_style_slugs():
    """Return all Style slugs."""
    return list(Style.objects.all().order_by('slug').values_list('slug', flat=True))
