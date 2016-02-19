from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = 'chiton.closet'
    label = 'chiton_closet'
    verbose_name = _('Closet')
