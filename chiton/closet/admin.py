from django import db, forms
from django.contrib import admin
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


@admin.register(models.Garment, site=site)
class GarmentAdmin(admin.ModelAdmin):

    inlines = [AffiliateItemInline]
    list_display = ('name', 'brand', 'basic', 'affiliate_view_links')
    list_filter = ('basic',)
    ordering = ('name',)
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': ('name', 'brand', 'basic')
        }),
        (_('Weighting'), {
            'fields': ('formalities', 'styles', 'shoulder_emphasis', 'waist_emphasis', 'hip_emphasis')
        }),
        (_('Dimensions'), {
            'fields': ('sleeve_length', 'bottom_length', 'pant_rise', 'is_busty', 'is_plus_sized')
        }),
        (_('Details'), {
            'fields': ('care', 'description', 'notes')
        })
    )

    formfield_overrides = {
        db.models.TextField: {'widget': forms.Textarea(attrs={'cols': 60, 'rows': 2})}
    }

    def affiliate_view_links(self, garment):
        affiliate_items = garment.affiliate_items.all().order_by('network__name')
        links = [
            '<a href="%s" target="_blank">%s</a>' % (i.url, i.network)
            for i in affiliate_items
        ]
        return format_html('<br>'.join(links))
    affiliate_view_links.short_description = _('Links')
