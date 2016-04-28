from rest_framework import viewsets

from chiton.api.serializers import WardrobeProfileSerializer
from chiton.wintour.models import WardrobeProfile


class WardrobeProfileViewSet(viewsets.ModelViewSet):
    queryset = WardrobeProfile.objects.all()
    serializer_class = WardrobeProfileSerializer
