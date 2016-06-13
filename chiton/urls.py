from django.conf.urls import include, url

from chiton.core import admin

urlpatterns = [
    url(r'^api/', include('chiton.api.urls')),
    url(r'^stockroom/', admin.site.urls)
]
