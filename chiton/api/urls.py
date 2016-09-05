from django.conf import settings
from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from chiton.api import views


patterns = [
    url(r'^recommendations/$', views.Recommendations.as_view()),
    url(r'^wardrobe-profiles/$', views.WardrobeProfiles.as_view())
]

if settings.CHITON_ALLOW_API_BROWSING:
    patterns += [
        url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]

urlpatterns = format_suffix_patterns(patterns)
