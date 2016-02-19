from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class AdminSite(admin.AdminSite):

    site_header = _("Chiton")
    site_title = _("Chiton")
    index_title = _("Chiton administration")


site = AdminSite(name="chiton")
