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
