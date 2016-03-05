from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from chiton.closet import models
from chiton.core.admin import site


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

    list_display = ('name', 'brand')
    list_filter = ('brand',)
    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.Style, site=site)
class StyleAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
