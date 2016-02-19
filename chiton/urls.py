from django.conf.urls import url

from chiton.core import admin

urlpatterns = [
    url(r'^stockroom/', admin.site.urls),
]
