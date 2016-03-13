from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from chiton.runway import models
from chiton.core.admin import site


@admin.register(models.Formality, site=site)
class FormalityAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('name',)


@admin.register(models.Style, site=site)
class StyleAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
