from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from chiton.core.admin import site
from chiton.runway import models


class ProprietyInline(admin.TabularInline):

    model = models.Propriety


@admin.register(models.Basic, site=site)
class BasicAdmin(admin.ModelAdmin):

    inlines = (ProprietyInline,)
    list_display = ('name',)


@admin.register(models.Formality, site=site)
class FormalityAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('name',)


@admin.register(models.Propriety, site=site)
class ProprietyAdmin(admin.ModelAdmin):

    list_display = ('basic', 'formality', 'weight')


@admin.register(models.Style, site=site)
class StyleAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
