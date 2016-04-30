from adminsortable2.admin import SortableAdminMixin
from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

from chiton.core.admin import site
from chiton.runway import models


class ProprietyInline(admin.TabularInline):

    model = models.Propriety


@admin.register(models.Basic, site=site)
class BasicAdmin(admin.ModelAdmin):

    inlines = (ProprietyInline,)
    list_display = ('name', 'category')
    list_filter = ('category',)

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^proprieties-table/$', self.admin_site.admin_view(self.proprieties_table), name='basic-proprieties-table')
        ]
        return custom + core

    def proprieties_table(self, request):
        basics = models.Basic.objects.all()
        formalities = models.Formality.objects.all()

        basic_data = []
        for basic in basics:
            proprieties = models.Propriety.objects.filter(basic=basic)
            importances = []
            for formality in formalities:
                display = ''
                weight = ''
                for propriety in proprieties:
                    if propriety.formality == formality:
                        display = propriety.get_importance_display()
                        weight = propriety.importance
                importances.append({
                    'name': display,
                    'weight': weight
                })

            basic_data.append({
                'name': basic.name,
                'category': basic.category.name,
                'importances': importances
            })

        return TemplateResponse(request, 'admin/chiton_runway/basic/proprieties_table.html', dict(
            self.admin_site.each_context(request),
            basics=basic_data,
            formalities=formalities,
            title=_('Basics grid')
        ))


@admin.register(models.Category, site=site)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ('name',)


@admin.register(models.Formality, site=site)
class FormalityAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ('name',)


@admin.register(models.Propriety, site=site)
class ProprietyAdmin(admin.ModelAdmin):

    list_display = ('basic', 'formality', 'importance')


@admin.register(models.Style, site=site)
class StyleAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
