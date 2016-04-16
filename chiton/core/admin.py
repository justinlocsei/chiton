from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_control
from django.views.i18n import javascript_catalog


class AdminSite(admin.AdminSite):

    site_header = _('Cover Your Basics (%(environment)s)') % {'environment': settings.ENVIRONMENT_NAME.capitalize()}
    site_title = _('Cover Your Basics')

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^jsi18n/$', self.cached_jsi18n, name='jsi18n')
        ]
        return custom + core

    @cache_control(private=True, max_age=60 * 60 * 24)
    def cached_jsi18n(self, request):
        return javascript_catalog(request, packages=['django.conf', 'django.contrib.admin'])


site = AdminSite(name='chiton')
