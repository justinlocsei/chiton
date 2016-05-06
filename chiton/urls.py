from django.conf.urls import include, url

from chiton.core import admin

urlpatterns = [
    url(r'^stockroom/', admin.site.urls)
]
