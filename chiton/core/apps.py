from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = "chiton.core"
    label = "chiton"
    verbose_name = _("Core")
