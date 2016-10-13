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
from chiton.closet.models import StandardSize
from chiton.core.admin import site
from chiton.rack.apps import Config as RackConfig
from chiton.runway.models import Basic, Formality, Style
from chiton.wintour import models
from chiton.wintour.data import BODY_SHAPE_CHOICES, EXPECTATION_FREQUENCY_CHOICES
from chiton.wintour.matching import make_recommendations
from chiton.wintour.pipelines.core import CorePipeline
from chiton.wintour.profiles import PipelineProfile


# A regex for formality expectations as exposed via GET params
FORMALITY_PARAM_MATCH = re.compile(r'formality\[([^\]]+)\]')


class FormalityExpectationInline(admin.TabularInline):
    model = models.FormalityExpectation


class UnwantedCareTypeInline(admin.TabularInline):
    model = models.UnwantedCareType


@admin.register(models.Person, site=site)
class PersonAdmin(admin.ModelAdmin):

    list_display = ('email', 'joined')
    ordering = ('-joined',)

    def email(self, person):
        return person.email
    email.short_description = _('Email')


@admin.register(models.WardrobeProfile, site=site)
class WardrobeProfileAdmin(admin.ModelAdmin):

    inlines = [FormalityExpectationInline, UnwantedCareTypeInline]
    list_display = ('pk', 'created_at', 'birth_year', 'body_shape', 'recommendations')
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
            'avoid_care': [c.care for c in profile.unwanted_care_types.all()],
            'birth_year': profile.birth_year,
            'body_shape': profile.body_shape,
            'size': [s.slug for s in profile.sizes.all()],
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
            recs_dict = make_recommendations(profile, CorePipeline(), debug=True)
        else:
            profile = None
            recs_dict = {}

        # Add information on the available and selected styles
        styles = []
        for style in Style.objects.all():
            selected = False
            if profile:
                selected = style.slug in profile['styles']

            styles.append({
                'name': style.name,
                'selected': selected,
                'slug': style.slug
            })

        # Build a lookup table of expectations
        expectations = {}
        if profile:
            for expectation in profile['expectations']:
                expectations[expectation['formality']] = expectation['frequency']

        # Add information on the available and selected formality expectations
        formalities = []
        for formality in Formality.objects.all():
            frequency = None
            if profile:
                frequency = expectations.get(formality.slug, None)

            formalities.append({
                'frequency': frequency,
                'name': formality.name,
                'slug': formality.slug
            })

        # Respect filter information specified via GET params
        selected_sizes = {}
        selected_basics = {}
        avoid_care = {}
        cutoff = None
        if request.GET:
            cutoff = request.GET.get('cutoff', None)

            basic_params = request.GET.getlist('basic', [])
            if basic_params:
                for basic_slug in basic_params:
                    selected_basics[basic_slug] = True

            size_params = request.GET.getlist('size', [])
            if size_params:
                for size_slug in size_params:
                    selected_sizes[size_slug] = True

            care_params = request.GET.getlist('avoid_care', [])
            if care_params:
                for care_id in care_params:
                    avoid_care[care_id] = True

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

        # Add information on the available and selected sizes
        sizes = []
        for size in StandardSize.objects.all():
            selected = False
            if selected_sizes:
                selected = selected_sizes.get(size.slug, False)

            sizes.append({
                'name': size.display_name,
                'selected': selected,
                'slug': size.slug
            })

        return TemplateResponse(request, 'admin/chiton_wintour/wardrobeprofile/recommendations_visualizer.html', dict(
            self.admin_site.each_context(request),
            avoid_care=avoid_care,
            basics=basics,
            body_shape_choices=BODY_SHAPE_CHOICES,
            cutoff=cutoff,
            frequency_choices=EXPECTATION_FREQUENCY_CHOICES,
            formalities=formalities,
            recommendations_json=json.dumps(self._add_admin_urls_to_recs(recs_dict)),
            profile=profile,
            sizes=sizes,
            styles=styles,
            title='Recommendations Visualizer'
        ))

    def recalculate_recommendations(self, request):
        """Return recalculate recommendations based on request data as JSON."""
        profile = self._convert_get_params_to_pipeline_profile(request.GET)
        recs_dict = make_recommendations(profile, CorePipeline(), debug=True)

        return JsonResponse(self._add_admin_urls_to_recs(recs_dict))

    def _convert_get_params_to_pipeline_profile(self, get_data):
        """Use the values from GET data to create a new pipeline profile."""
        expectations = []
        for param in get_data:
            formality_match = FORMALITY_PARAM_MATCH.match(param)
            if formality_match:
                expectations.append({
                    'formality': formality_match.group(1),
                    'frequency': get_data[param]
                })

        return PipelineProfile({
            'avoid_care': get_data.getlist('avoid_care'),
            'birth_year': int(get_data['birth_year']),
            'body_shape': get_data['body_shape'],
            'expectations': expectations,
            'sizes': get_data.getlist('size'),
            'styles': get_data.getlist('style')
        })

    def _add_admin_urls_to_recs(self, recs):
        """Add admin-site URLs to each garment in a recommendations dict."""
        basics = recs.get('basics', {})

        for basic in basics:
            for garment in basic['garments']:
                garment['edit_url'] = reverse(
                    'admin:%s_garment_change' % ClosetConfig.label,
                    args=[garment['garment']['id']]
                )

                for purchase_option in garment['purchase_options']:
                    item_edit_url = reverse(
                        'admin:%s_affiliateitem_change' % RackConfig.label,
                        args=[purchase_option['id']]
                    )
                    item_api_url = reverse(
                        'admin:affiliate-item-api-details',
                        args=[purchase_option['id']]
                    )
                    affiliate_links = [
                        {'name': '%s API' % purchase_option['network_name'], 'url': item_api_url},
                        {'name': 'Edit Item', 'url': item_edit_url}
                    ]

                    purchase_option['admin_links'] = affiliate_links

        return recs
