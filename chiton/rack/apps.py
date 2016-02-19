from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = 'chiton.rack'
    label = 'chiton_rack'
    verbose_name = _('Rack')
