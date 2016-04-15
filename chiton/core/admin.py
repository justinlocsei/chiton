from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class AdminSite(admin.AdminSite):

    site_header = _('Cover Your Basics (%(environment)s)') % {'environment': settings.ENVIRONMENT_NAME.capitalize()}
    site_title = _('Cover Your Basics')


site = AdminSite(name='chiton')
