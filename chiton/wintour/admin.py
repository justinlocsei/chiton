from django.conf.urls import url
from django.contrib import admin
from django.template.response import TemplateResponse
import json

from chiton.core.admin import site
from chiton.runway.models import Basic, Formality, Style
from chiton.wintour import models
from chiton.wintour.data import BODY_SHAPE_CHOICES, EXPECTATION_FREQUENCY_CHOICES
from chiton.wintour.matching import make_recommendations, package_wardrobe_profile, serialize_recommendations


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
        pipeline_profile = package_wardrobe_profile(profile)
        recs = make_recommendations(pipeline_profile)
        recs_dict = serialize_recommendations(recs)

        profile_styles = [style.pk for style in profile.styles.all()]

        styles = []
        for style in Style.objects.all():
            styles.append({
                'name': style.name,
                'pk': style.pk,
                'selected': style.pk in profile_styles
            })

        expectation_map = {}
        for expectation in profile.expectations.all():
            expectation_map[expectation.formality.pk] = expectation.frequency

        formalities = []
        for formality in Formality.objects.all():
            formalities.append({
                'frequency': expectation_map.get(formality.pk, None),
                'name': formality.name,
                'pk': formality.pk
            })

        basics = []
        for basic in Basic.objects.all():
            basics.append({
                'name': basic.name,
                'pk': basic.pk,
                'selected': True
            })

        return TemplateResponse(request, 'admin/chiton_wintour/wardrobeprofile/recommendations.html', dict(
            self.admin_site.each_context(request),
            basics=basics,
            body_shape_choices=BODY_SHAPE_CHOICES,
            frequency_choices=EXPECTATION_FREQUENCY_CHOICES,
            formalities=formalities,
            recommendations_json=json.dumps(recs_dict),
            styles=styles,
            title='Recommendations Visualizer',
            wardrobe_profile=profile
        ))
