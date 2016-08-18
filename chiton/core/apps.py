from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class Config(AppConfig):

    name = 'chiton.core'
    label = 'chiton'
    verbose_name = _('Core')

    def ready(self):
        """Bind signal handlers for cached queries when the app is ready."""
        from chiton.core.queries import bind_signal_handlers
        bind_signal_handlers()
