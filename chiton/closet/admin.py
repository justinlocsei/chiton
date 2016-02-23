from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from chiton.closet import models
from chiton.core.admin import site


@admin.register(models.Garment, site=site)
class GarmentAdmin(admin.ModelAdmin):

    list_display = ('name', 'brand', 'category')
    list_filter = ('brand', 'category')
    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.Brand, site=site)
class BrandAdmin(admin.ModelAdmin):

    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.GarmentCategory, site=site)
class GarmentCategoryAdmin(MPTTModelAdmin):
    pass


@admin.register(models.GarmentOption, site=site)
class GarmentOptionAdmin(admin.ModelAdmin):
    pass
