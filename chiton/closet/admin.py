from django.contrib import admin

from chiton.closet import models
from chiton.core.admin import site


@admin.register(models.Garment, site=site)
class GarmentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Brand, site=site)
class BrandAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Line, site=site)
class LineAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GarmentCategory, site=site)
class GarmentCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.GarmentOption, site=site)
class GarmentOptionAdmin(admin.ModelAdmin):
    pass
