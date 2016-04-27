from django.conf.urls import include, url

from chiton.api.urls import urlpatterns as api_urls
from chiton.core import admin

urlpatterns = [
    url(r'^api/', include(api_urls)),
    url(r'^stockroom/', admin.site.urls)
]
