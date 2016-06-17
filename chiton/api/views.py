from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chiton.core.exceptions import FormatError
from chiton.wintour.matching import make_recommendations
from chiton.wintour.models import Recommendation
from chiton.wintour.pipelines.core import CorePipeline
from chiton.wintour.profiles import PipelineProfile


class Recommendations(APIView):
    """Manage outfit recommendations."""

    def post(self, request, format=None):
        """Generate recommendations for a user."""
        try:
            profile = PipelineProfile(request.data, validate=True)
        except FormatError as e:
            return Response({'errors': e.fields }, status=status.HTTP_400_BAD_REQUEST)

        Recommendation.objects.create(profile=profile)

        recommendations = make_recommendations(profile, CorePipeline())
        return Response(recommendations)
