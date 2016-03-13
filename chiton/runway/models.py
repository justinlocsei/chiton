from autoslug import AutoSlugField
from django.db import models
from django.utils.translation import ugettext_lazy as _


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
