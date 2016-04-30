from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse
import json
import pygments
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from chiton.core.admin import site
from chiton.wintour import models
from chiton.wintour.matching import make_recommendations


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

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^(?P<pk>\d+)/recommendations/$', self.admin_site.admin_view(self.recommendations), name='wardrobe-profile-recommendations')
        ]
        return custom + core

    def recommendations(self, request, pk):
        profile = models.WardrobeProfile.objects.get(pk=pk)
        recs_dict = make_recommendations(profile, serialize=True)

        profile_dict = {
            'age': profile.age,
            'expectations': [
                {'formality': e.formality.name, 'frequency': e.frequency}
                for e in profile.expectations.all()
            ],
            'shape': profile.shape,
            'styles': sorted([s.name for s in profile.styles.all()]),
        }

        return TemplateResponse(request, 'admin/chiton_wintour/wardrobeprofile/recommendations.html', dict(
            self.admin_site.each_context(request),
            wardrobe_profile_json=_dict_as_highlighted_json(profile_dict),
            recommendations_json=_dict_as_highlighted_json(recs_dict),
            highlight_styles=HtmlFormatter().get_style_defs('.highlight'),
            item=profile,
            title='Recommendations for Wardrobe Profile %s' % pk
        ))


def _dict_as_highlighted_json(value):
    """Convert a dict to a highlighted JSON string.

    Args:
        value (dict): A dictionary instance

    Returns:
        str: The dict as highlighted JSON
    """
    as_json = json.dumps(value, sort_keys=True, indent=4)
    return pygments.highlight(as_json, JsonLexer(), HtmlFormatter())
