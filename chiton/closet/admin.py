from adminsortable2.admin import SortableAdminMixin
from django import db, forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from chiton.closet import models
from chiton.closet.apps import Config as ClosetConfig
from chiton.core.admin import site
from chiton.rack.admin import AffiliateItemInline
from chiton.rack.apps import Config as RackConfig
from chiton.rack.models import AffiliateItem, StockRecord
from chiton.rack.affiliates.data import update_affiliate_item_details


@admin.register(models.Brand, site=site)
class BrandAdmin(admin.ModelAdmin):

    list_display = ('name', 'age_lower', 'age_upper')
    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.CanonicalSize, site=site)
class CanonicalSizeAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('name', 'range_lower', 'range_upper')
    ordering = ('position',)


@admin.register(models.Color, site=site)
class ColorAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)


@admin.register(models.Garment, site=site)
class GarmentAdmin(admin.ModelAdmin):

    inlines = [AffiliateItemInline]
    list_display = ('name', 'brand', 'basic', 'affiliate_view_links', 'created_at', 'updated_at')
    list_filter = ('basic',)
    ordering = ('name',)
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': ('name', 'brand', 'basic')
        }),
        (_('Weighting'), {
            'fields': ('formalities', 'styles', 'shoulder_emphasis', 'waist_emphasis', 'hip_emphasis', 'is_featured')
        }),
        (_('Dimensions'), {
            'fields': ('sleeve_length', 'bottom_length', 'pant_rise', 'is_busty', 'is_regular_sized', 'is_plus_sized', 'is_tall_sized', 'is_petite_sized')
        }),
        (_('Details'), {
            'fields': ('care',)
        })
    )

    formfield_overrides = {
        db.models.TextField: {'widget': forms.Textarea(attrs={'cols': 60, 'rows': 2})}
    }

    def affiliate_view_links(self, garment):
        links = []

        affiliate_items = garment.affiliate_items.all().order_by('network__name')
        for item in affiliate_items:
            api_url = reverse('admin:affiliate-item-api-details', args=[item.pk])
            links.append(item.network.name)
            links.append('<a href="%s" target="_blank">Item</a> | <a href="%s" target="_blank">API</a>' % (item.url, api_url))

        return format_html('<br>'.join(links))
    affiliate_view_links.short_description = _('Links')

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        for affiliate_item in form.instance.affiliate_items.all():
            update_affiliate_item_details(affiliate_item)

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^availability/$', self.admin_site.admin_view(self.availability), name='garment-availability')
        ]
        return custom + core

    def availability(self, request):
        item_records = {}
        for record in StockRecord.objects.all().select_related('size'):
            item_records.setdefault(record.item_id, {
                'regular': 0,
                'tall': 0,
                'petite': 0,
                'plus': 0
            })
            if not record.is_available:
                continue

            item_record = item_records[record.item_id]
            if record.size.is_regular:
                item_record['regular'] += 1
            if record.size.is_tall:
                item_record['tall'] += 1
            if record.size.is_petite:
                item_record['petite'] += 1
            if record.size.is_plus_sized:
                item_record['plus'] += 1

        items = []
        for item in AffiliateItem.objects.all().select_related('garment', 'network'):
            if not item_records[item.pk]:
                continue

            change_url = reverse('admin:%s_affiliateitem_change' % RackConfig.label, args=[item.pk])
            garment_change_url = reverse('admin:%s_garment_change' % ClosetConfig.label, args=[item.garment.pk])

            item_record = item_records[item.pk]
            items.append(dict(item_record,
                change_url=change_url,
                garment=item.garment.name,
                garment_change_url=garment_change_url,
                name=item.name,
                network=item.network.name,
                total=sum(item_record.values())
            ))

        return TemplateResponse(request, 'admin/chiton_closet/garment/availability.html', dict(
            self.admin_site.each_context(request),
            items=sorted(items, key=lambda i: i['total'], reverse=True),
            title='Garment Availability'
        ))


@admin.register(models.StandardSize, site=site)
class StandardSizeAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('canonical', 'is_tall', 'is_petite', 'is_plus_sized')
    ordering = ('position',)
