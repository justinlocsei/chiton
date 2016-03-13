from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from chiton.closet import models
from chiton.core.admin import site
from chiton.rack.admin import AffiliateItemInline


@admin.register(models.Brand, site=site)
class BrandAdmin(admin.ModelAdmin):

    list_display = ('name', 'age_lower', 'age_upper')
    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.Formality, site=site)
class FormalityAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('name',)


@admin.register(models.Garment, site=site)
class GarmentAdmin(admin.ModelAdmin):

    inlines = [AffiliateItemInline]
    list_display = ('name', 'brand')
    list_filter = ('brand',)
    ordering = ('name',)
    search_fields = ['name']

    fieldsets = (
        (None, {
            'fields': ('name', 'brand')
        }),
        (_('Weighting'), {
            'fields': ('formalities', 'styles', 'shoulder_emphasis', 'waist_emphasis', 'hip_emphasis')
        }),
        (_('Dimensions'), {
            'fields': ('sleeve_length', 'bottom_length', 'pant_rise', 'is_busty')
        }),
        (_('Details'), {
            'fields': ('description', 'notes')
        })
    )


@admin.register(models.Style, site=site)
class StyleAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
