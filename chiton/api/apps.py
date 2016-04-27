from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = 'chiton.api'
    label = 'chiton_api'
    verbose_name = _('API')
