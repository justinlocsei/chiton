import json
import re
from urllib.parse import urlencode

from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from chiton.closet.apps import Config as ClosetConfig
from chiton.core.admin import site
from chiton.runway.models import Basic, Formality, Style
from chiton.wintour import models
from chiton.wintour.data import BODY_SHAPE_CHOICES, EXPECTATION_FREQUENCY_CHOICES
from chiton.wintour.matching import make_recommendations, serialize_recommendations
from chiton.wintour.pipeline import PipelineProfile


# A regex for formality expectations as exposed via GET params
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
    list_display = ('pk', 'created_at', 'age', 'body_shape', 'recommendations')
    list_display_links = ('pk', 'created_at')
    ordering = ('-created_at',)

    def recommendations(self, profile):
        url = reverse('admin:wardrobe-profile-recommendations', args=[profile.pk])
        link = '<a href="%s">View Recommendations</a>' % url
        return format_html(link)
    recommendations.short_description = _('Recommendations')

    def get_urls(self):
        core = super().get_urls()
        custom = [
            url(r'^recommendations-visualizer/$', self.admin_site.admin_view(self.recommendations_visualizer), name='recommendations-visualizer'),
            url(r'^recommendations-visualizer/recalculate$', self.admin_site.admin_view(self.recalculate_recommendations), name='recalculate-recommendations'),
            url(r'^(?P<pk>\d+)/recommendations/$', self.admin_site.admin_view(self.wardrobe_profile_recommendations), name='wardrobe-profile-recommendations')
        ]
        return custom + core

    def wardrobe_profile_recommendations(self, request, pk):
        """Redirect to the visualizer, seeded with the profile's data."""
        profile = models.WardrobeProfile.objects.get(pk=pk)

        data = {
            'age': profile.age,
            'body_shape': profile.body_shape,
            'style': [s.slug for s in profile.styles.all()]
        }
        for expectation in profile.expectations.all().select_related('formality'):
            data['formality[%s]' % expectation.formality.slug] = expectation.frequency

        visualizer_url = reverse('admin:recommendations-visualizer')
        query_string = urlencode(data, doseq=True)

        return redirect('%s?%s' % (visualizer_url, query_string))

    def recommendations_visualizer(self, request):
        """Show an interactive visualizer for recommendations."""
        if request.GET:
            profile = self._convert_get_params_to_pipeline_profile(request.GET)
            recs = make_recommendations(profile, debug=True)
            recs_dict = serialize_recommendations(recs)
        else:
            profile = None
            recs_dict = {}

        # Add information on the available and selected styles
        styles = []
        for style in Style.objects.all():
            selected = False
            if profile:
                selected = style.slug in profile.styles

            styles.append({
                'name': style.name,
                'selected': selected,
                'slug': style.slug
            })

        # Add information on the available and selected formality expectations
        formalities = []
        for formality in Formality.objects.all():
            frequency = None
            if profile:
                frequency = profile.expectations.get(formality.slug, None)

            formalities.append({
                'frequency': frequency,
                'name': formality.name,
                'slug': formality.slug
            })

        # Respect filter information specified via GET params
        selected_basics = None
        cutoff = None
        if request.GET:
            cutoff = request.GET.get('cutoff', None)

            basic_params = request.GET.getlist('basic', [])
            if basic_params:
                selected_basics = {}
                for basic_slug in basic_params:
                    selected_basics[basic_slug] = True

        # Add information on the available and selected basics
        basics = []
        for basic in Basic.objects.all():
            selected = True
            if selected_basics:
                selected = selected_basics.get(basic.slug, False)

            basics.append({
                'name': basic.name,
                'selected': selected,
                'slug': basic.slug
            })

        return TemplateResponse(request, 'admin/chiton_wintour/wardrobeprofile/recommendations_visualizer.html', dict(
            self.admin_site.each_context(request),
            basics=basics,
            body_shape_choices=BODY_SHAPE_CHOICES,
            cutoff=cutoff,
            frequency_choices=EXPECTATION_FREQUENCY_CHOICES,
            formalities=formalities,
            recommendations_json=json.dumps(self._add_admin_urls_to_recs(recs_dict)),
            profile=profile,
            styles=styles,
            title='Recommendations Visualizer'
        ))

    def recalculate_recommendations(self, request):
        """Return recalculate recommendations based on request data as JSON."""
        profile = self._convert_get_params_to_pipeline_profile(request.GET)
        recs_dict = make_recommendations(profile, debug=True)
        serialized = serialize_recommendations(recs_dict)

        return JsonResponse(self._add_admin_urls_to_recs(serialized))

    def _convert_get_params_to_pipeline_profile(self, get_data):
        """Use the values from GET data to create a new pipeline profile."""
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

    def _add_admin_urls_to_recs(self, recs):
        """Add admin-site URLs to each garment in a recommendations dict."""
        for basic, data in recs['basics'].items():
            for garment in data['garments']:
                url = reverse(
                    'admin:%s_garment_change' % ClosetConfig.label,
                    args=[garment['garment']['pk']]
                )
                garment['urls']['admin'] = [{'name': 'Garment', 'url': url}]

        return recs
