from rest_framework.permissions import BasePermission

from chiton.wintour.apps import Config as Wintour
from chiton.wintour.models import Recommendation, WardrobeProfile


class IsRecommender(BasePermission):
    """A check for whether the user can create recommendations."""

    CREATED_MODELS = (Recommendation, WardrobeProfile)

    def has_permission(self, request, view):
        """Grant access to users with control over recommendation models."""
        permissions = [
            '%s.add_%s' % (Wintour.label, model.__name__.lower())
            for model in self.CREATED_MODELS
        ]
        return request.user.has_perms(permissions)
