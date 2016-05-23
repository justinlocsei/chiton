from adminsortable2.admin import SortableAdminMixin
from django import db, forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from chiton.closet import models
from chiton.core.admin import site
from chiton.rack.admin import AffiliateItemInline


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


@admin.register(models.StandardSize, site=site)
class StandardSizeAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('canonical', 'is_tall', 'is_petite', 'is_plus_sized')
    ordering = ('position',)
