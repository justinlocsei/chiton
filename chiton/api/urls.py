from django.conf.urls import include, url
from rest_framework import routers

from chiton.api import views


router = routers.DefaultRouter()
router.register(r'wardrobe-profiles', views.WardrobeProfileViewSet)

urlpatterns = [
    url(r'^', include(router.urls))
]
