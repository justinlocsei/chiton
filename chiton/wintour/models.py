from django.contrib.postgres.fields import JSONField
from django.db import connection, models
from django.utils.translation import ugettext_lazy as _
from email_validator import EmailNotValidError, validate_email

from chiton.core.encryption import decrypt, encrypt
from chiton.core.queries import cache_query
from chiton.closet.data import CARE_CHOICES
from chiton.closet.models import StandardSize
from chiton.runway.models import Formality, Style
from chiton.wintour import data


class PersonManager(models.Manager):
    """A custom manager for people."""

    def ensure_exists_with_email(self, email):
        """Ensure that a person exists with a given email address.

        Args:
            email (str): An email address

        Returns:
            chiton.wintour.models.Person: The new or existing person
        """
        try:
            normalized = validate_email(email, check_deliverability=False)['email']
        except EmailNotValidError:
            normalized = email

        email_lookup = _get_person_email_map()
        person_id = email_lookup.get(normalized, None)

        if person_id:
            return self.get(pk=person_id)
        else:
            return self.create(email=normalized)

    def list_email_addresses(self):
        """Get a list of all email addresses.

        Returns:
            list[str]: All email addresses
        """
        emails = [p.email for p in self.all()]
        return [email for email in emails if email]

    def clear_email_addresses(self):
        """Clear the email addresses of all stored people.

        Returns:
            int: The number of email addresses cleared

        """
        previous_emails = set(self.values_list('encrypted_email', flat=True))

        # Null out the encrypted email directly via SQL, to bypass post-save
        # signals that might read the email with an invalid encryption key
        with connection.cursor() as cursor:
            cursor.execute('UPDATE ' + self.model._meta.db_table + ' SET encrypted_email = %s', [''])

        # Re-save each person using Django's ORM, in order to trigger any
        # post-save signals and refresh associated data
        for person in self.all():
            person.save()

        current_emails = set(self.values_list('encrypted_email', flat=True))

        return len(previous_emails - current_emails)


class Person(models.Model):
    """A person who can receive recommendations."""

    objects = PersonManager()

    first_name = models.CharField(max_length=255, verbose_name=_('first name'), null=True, blank=True)
    last_name = models.CharField(max_length=255, verbose_name=_('last name'), null=True, blank=True)
    encrypted_email = models.TextField(verbose_name=_('encrypted email'))
    joined = models.DateTimeField(verbose_name=_('joined'), auto_now_add=True)

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
        return ' '.join([p or '' for p in parts if p])

    @property
    def email(self):
        """The user's email address.

        Returns:
            str: A decrypted email address
        """
        if self.encrypted_email:
            return decrypt(self.encrypted_email)
        else:
            return None

    @email.setter
    def email(self, value):
        """Encrypt the user's email address.

        Args:
            value (str): A non-encrypted email address
        """
        self.encrypted_email = encrypt(value)


class FormalityExpectation(models.Model):
    """How often a level of formality is expected for a profile."""

    profile = models.ForeignKey('WardrobeProfile', on_delete=models.CASCADE, verbose_name=_('wardrobe profile'), related_name='expectations')
    formality = models.ForeignKey(Formality, on_delete=models.CASCADE, verbose_name=_('level of formality'))
    frequency = models.CharField(max_length=25, choices=data.EXPECTATION_FREQUENCY_CHOICES, verbose_name=_('frequency'))

    class Meta:
        verbose_name = _('formality expectation')
        verbose_name_plural = _('formality expectations')


class UnwantedCareType(models.Model):
    """An unwanted care type for a garment."""

    profile = models.ForeignKey('WardrobeProfile', on_delete=models.CASCADE, verbose_name=_('wardrobe profile'), related_name='unwanted_care_types')
    care = models.CharField(max_length=25, choices=CARE_CHOICES, verbose_name=_('care instructions'))

    class Meta:
        verbose_name = _('unwanted care type')
        verbose_name_plural = _('unwanted care types')


class WardrobeProfile(models.Model):
    """Data used to generate wardrobe recommendations."""

    body_shape = models.CharField(max_length=25, choices=data.BODY_SHAPE_CHOICES, verbose_name=_('body shape'))
    birth_year = models.PositiveSmallIntegerField(verbose_name=_('birth year'))
    styles = models.ManyToManyField(Style, verbose_name=_('styles'))
    sizes = models.ManyToManyField(StandardSize, verbose_name=_('sizes'))
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name=_('person'), null=True, blank=True)
    recommendation = models.ForeignKey('Recommendation', on_delete=models.SET_NULL, verbose_name=_('recommendation'), null=True, blank=True)

    class Meta:
        verbose_name = _('wardrobe profile')
        verbose_name_plural = _('wardrobe profiles')


class Recommendation(models.Model):
    """A set of wardrobe recommendations generated from a profile."""

    profile = JSONField(verbose_name=_('The profile data'))
    ip_address = models.GenericIPAddressField(verbose_name=_('IP address'), null=True, blank=True)
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('recommendation')
        verbose_name_plural = _('recommendations')


@cache_query(Person)
def _get_person_email_map():
    """Return a map of email addresses to Person IDs."""
    lookup = {}

    for person in Person.objects.all():
        lookup[person.email] = person.pk

    return lookup
