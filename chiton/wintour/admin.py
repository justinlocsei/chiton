from django.conf.urls import url
from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
import json
import re

from chiton.core.admin import site
from chiton.runway.models import Basic, Formality, Style
from chiton.wintour import models
from chiton.wintour.data import BODY_SHAPE_CHOICES, EXPECTATION_FREQUENCY_CHOICES
from chiton.wintour.matching import make_recommendations, package_wardrobe_profile, serialize_recommendations
from chiton.wintour.pipeline import PipelineProfile


FORMALITY_PARAM_MATCH = re.compile(r'formality\[([^\]]+)\]')


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
        pre = [
            url(r'^recommendations-visualizer/$', self.admin_site.admin_view(self.recommendations_visualizer), name='recommendations-visualizer'),
            url(r'^recommendations-visualizer/recalculate$', self.admin_site.admin_view(self.recalculate_recommendations), name='recalculate-recommendations')
        ]
        post = [
            url(r'^(?P<pk>\d+)/recommendations/$', self.admin_site.admin_view(self.wardrobe_profile_recommendations), name='wardrobe-profile-recommendations')
        ]
        return pre + core + post

    def wardrobe_profile_recommendations(self, request, pk):
        wardrobe_profile = models.WardrobeProfile.objects.get(pk=pk)
        profile = package_wardrobe_profile(wardrobe_profile)

    def recommendations_visualizer(self, request):
        profile = self._convert_get_params_to_pipeline_profile(request.GET)
        recs = make_recommendations(profile)
        recs_dict = serialize_recommendations(recs)

        styles = []
        for style in Style.objects.all():
            styles.append({
                'name': style.name,
                'selected': style.slug in profile.styles,
                'slug': style.slug
            })

        formalities = []
        for formality in Formality.objects.all():
            formalities.append({
                'frequency': profile.expectations.get(formality.slug, None),
                'name': formality.name,
                'slug': formality.slug
            })

        basics = []
        for basic in Basic.objects.all():
            basics.append({
                'name': basic.name,
                'selected': True,
                'slug': basic.slug
            })

        return TemplateResponse(request, 'admin/chiton_wintour/wardrobeprofile/recommendations_visualizer.html', dict(
            self.admin_site.each_context(request),
            basics=basics,
            body_shape_choices=BODY_SHAPE_CHOICES,
            frequency_choices=EXPECTATION_FREQUENCY_CHOICES,
            formalities=formalities,
            recommendations_json=json.dumps(recs_dict),
            profile=profile,
            styles=styles,
            title='Recommendations Visualizer'
        ))

    def recalculate_recommendations(self, request):
        profile = self._convert_get_params_to_pipeline_profile(request.GET)
        recs = make_recommendations(profile)

        return JsonResponse(serialize_recommendations(recs))

    def _convert_get_params_to_pipeline_profile(self, get_data):
        expectations = {}
        for param in get_data:
            formality_match = FORMALITY_PARAM_MATCH.match(param)
            if formality_match:
                formality_slug = formality_match.group(1)
                expectations[formality_slug] = get_data[param]

        return PipelineProfile(
            age=int(get_data['age']),
            body_shape=get_data['body_shape'],
            expectations=expectations,
            styles=get_data.getlist('style')
        )
