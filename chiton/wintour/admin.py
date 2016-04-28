from django.contrib import admin

from chiton.core.admin import site
from chiton.wintour import models


class FormalityExpectationInline(admin.TabularInline):
    model = models.FormalityExpectation


@admin.register(models.Person, site=site)
class PersonAdmin(admin.ModelAdmin):

    list_display = ('first_name', 'last_name')
    ordering = ('last_name', 'first_name')


@admin.register(models.WardrobeProfile, site=site)
class WardrobeProfileAdmin(admin.ModelAdmin):

    inlines = [FormalityExpectationInline]
    list_display = ('created_at',)
    ordering = ('-created_at',)
