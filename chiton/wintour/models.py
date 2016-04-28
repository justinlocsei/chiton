from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.runway.models import Formality, Style
from chiton.wintour import data


def slug_for_person(person):
    """Generate the slug for a Person instance.

    Args:
        person (chiton.wintour.models.Person): A Person instance

    Returns:
        str: The slug for the person
    """
    return person.full_name


class Person(models.Model):
    """A person who can receive recommendations."""

    first_name = models.CharField(max_length=255, verbose_name=_('first name'))
    last_name = models.CharField(max_length=255, verbose_name=_('last name'))
    slug = AutoSlugField(max_length=255, populate_from=slug_for_person, verbose_name=_('slug'), unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))

    class Meta:
        ordering = ('last_name', 'first_name')
        verbose_name = _('person')
        verbose_name_plural = _('people')

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """The full name of the person.

        Returns:
            str: The person's full name
        """
        parts = [self.first_name, self.last_name]
        return ' '.join([p for p in parts if p])


class FormalityExpectation(models.Model):
    """How often a level of formality is expected for a profile."""

    profile = models.ForeignKey('WardrobeProfile', on_delete=models.CASCADE, verbose_name=_('wardrobe profile'))
    formality = models.ForeignKey(Formality, on_delete=models.CASCADE, verbose_name=_('level of formality'))
    frequency = models.CharField(max_length=25, choices=data.FORMALITY_FREQUENCY_CHOICES, verbose_name=_('frequency'))

    class Meta:
        verbose_name = _('formality expectation')
        verbose_name_plural = _('formality expectations')


class WardrobeProfile(models.Model):
    """Data used to generate wardrobe recommendations."""

    shape = models.CharField(max_length=25, choices=data.BODY_SHAPE_CHOICES, verbose_name=_('body shape'))
    age = models.PositiveSmallIntegerField(verbose_name=_('age'))
    styles = models.ManyToManyField(Style, verbose_name=_('styles'))
    formalities = models.ManyToManyField(Formality, verbose_name=_('formalities'), through=FormalityExpectation)
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), null=True, blank=True)

    class Meta:
        verbose_name = _('wardrobe profile')
        verbose_name_plural = _('wardrobe profiles')
