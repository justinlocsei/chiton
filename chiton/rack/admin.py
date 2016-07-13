from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
import json
import pygments
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from chiton.core.admin import site
from chiton.rack import models
from chiton.rack.affiliates import create_affiliate
from chiton.rack.forms import AffiliateItemURLForm


class StockRecordInline(admin.TabularInline):
    model = models.StockRecord


@admin.register(models.AffiliateItem, site=site)
class AffiliateItemAdmin(admin.ModelAdmin):

    form = AffiliateItemURLForm
    inlines = [StockRecordInline]
    list_display = ('name', 'network', 'item_link', 'api_link', 'price', 'has_detailed_stock', 'garment', 'retailer')
    list_filter = ('network', 'has_detailed_stock', 'retailer')
    ordering = ('name',)
    search_fields = ['name']

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^(?P<pk>\d+)/api/$', self.admin_site.admin_view(self.api_details), name='affiliate-item-api-details')
        ]
        return custom + core

    def api_details(self, request, pk):
        item = models.AffiliateItem.objects.get(pk=pk)

        affiliate = create_affiliate(slug=item.network.slug)
        overview = affiliate.request_raw(item.guid)

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

    def item_link(self, item):
        return format_html('<a href="%s" target="_blank">View Item</a>' % item.url)
    item_link.short_description = _('item page')

    def api_link(self, item):
        url = reverse('admin:affiliate-item-api-details', args=[item.pk])
        return format_html('<a href="%s" target="_blank">Query API</a>' % url)
    api_link.short_description = _('API details')


class AffiliateItemInline(admin.TabularInline):
    fields = ('network', 'url', 'guid', 'name')
    form = AffiliateItemURLForm
    model = models.AffiliateItem


@admin.register(models.AffiliateNetwork, site=site)
class AffiliateNetworkAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
