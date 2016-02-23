from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from chiton.closet import models
from chiton.core.admin import site


@admin.register(models.Garment, site=site)
class GarmentAdmin(admin.ModelAdmin):

    list_display = ('name', 'line', 'category')
    list_filter = ('line', 'category')
    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.Brand, site=site)
class BrandAdmin(admin.ModelAdmin):

    ordering = ('name',)
    search_fields = ['name']


@admin.register(models.Line, site=site)
class LineAdmin(admin.ModelAdmin):

    list_display = ('name', 'brand')
    list_filter = ('brand',)
    ordering = ('name', 'brand__name')


@admin.register(models.GarmentCategory, site=site)
class GarmentCategoryAdmin(MPTTModelAdmin):
    pass


@admin.register(models.GarmentOption, site=site)
class GarmentOptionAdmin(admin.ModelAdmin):
    pass
