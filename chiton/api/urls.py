from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from chiton.api import views


urlpatterns = format_suffix_patterns([
    url(r'^recommendations/$', views.Recommendations.as_view())
])
