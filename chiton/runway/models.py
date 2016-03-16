from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.runway import data


class BasicManager(models.Manager):
    """A custom manager for basics."""

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Basic(models.Model):
    """A basic role fulfilled by a garment."""

    objects = BasicManager()

    name = models.CharField(max_length=255, verbose_name=_('name'), unique=True)
    slug = AutoSlugField(max_length=255, populate_from='name', verbose_name=_('slug'), unique=True)
    category = models.ForeignKey('Category', verbose_name=_('category'))
    formalities = models.ManyToManyField('Formality', verbose_name=_('levels of formality'), through='Propriety')

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

    class Meta:
        ordering = ('name',)
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
