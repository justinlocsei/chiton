from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = 'chiton.wintour'
    label = 'chiton_wintour'
    verbose_name = _('Wintour')

    def ready(self):
        """Import all code that uses cached queries."""
        from chiton.wintour.pipelines.core import CorePipeline # noqa
