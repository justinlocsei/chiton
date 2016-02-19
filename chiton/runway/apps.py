from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = 'chiton.runway'
    label = 'chiton_runway'
    verbose_name = _('Runway')
