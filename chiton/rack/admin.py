from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
import json
import pygments
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from chiton.core.admin import site
from chiton.rack import models
from chiton.rack.affiliates import create_affiliate
from chiton.rack.forms import AffiliateItemURLForm


@admin.register(models.AffiliateItem, site=site)
class AffiliateItemAdmin(admin.ModelAdmin):

    form = AffiliateItemURLForm
    list_display = ('name', 'guid', 'network_name', 'created_at')
    list_filter = ('network',)
    ordering = ('created_at',)

    def network_name(self, obj):
        return obj.network.name
    network_name.admin_order_field = 'network__name'
    network_name.short_description = _('Affiliate Network')

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^(?P<pk>\d+)/api/$', self.admin_site.admin_view(self.api_details), name='affiliate-item-api-details')
        ]
        return custom + core

    def api_details(self, request, pk):
        item = models.AffiliateItem.objects.get(pk=pk)

        affiliate = create_affiliate(slug=item.network.slug)
        overview = affiliate.request_details(item.guid, display=True)

        api_response = json.dumps(overview, sort_keys=True, indent=4)
        api_json = pygments.highlight(api_response, JsonLexer(), HtmlFormatter())
        api_styles = HtmlFormatter().get_style_defs('.highlight')

        return TemplateResponse(request, 'admin/chiton_rack/affiliateitem/api_details.html', dict(
            self.admin_site.each_context(request),
            api_response_json=api_json,
            api_response_styles=api_styles,
            item=item,
            title=item.name
        ))


@admin.register(models.AffiliateNetwork, site=site)
class AffiliateNetworkAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
