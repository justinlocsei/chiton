from django.db import models
from django.utils.translation import ugettext_lazy as _

from chiton.closet.data import EMPHASES, EMPHASIS_CHOICES


class EmphasisField(models.SmallIntegerField):
    """A field to store a numeric emphasis."""

    description = _('An emphasis')

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = EMPHASIS_CHOICES
        if 'default' not in kwargs:
            kwargs['default'] = EMPHASES['NEUTRAL']

        super().__init__(*args, **kwargs)


class PriceField(models.DecimalField):
    """A field for storing a price for an article of clothing."""

    description = _('A price')

    def __init__(self, *args, **kwargs):
        options = {}
        options.update({'max_digits': 8, 'decimal_places': 2})
        options.update(kwargs)

        super().__init__(*args, **options)
