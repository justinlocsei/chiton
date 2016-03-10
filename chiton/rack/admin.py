from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from chiton.core.admin import site
from chiton.rack import models


@admin.register(models.AffiliateItem, site=site)
class AffiliateItemAdmin(admin.ModelAdmin):

    list_display = ('network_name', 'created_at')
    ordering = ('created_at',)

    def network_name(self, obj):
        return obj.network.name
    network_name.admin_order_field = 'network__name'
    network_name.short_description = _('Affiliate Network')


@admin.register(models.AffiliateNetwork, site=site)
class AffiliateNetworkAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
