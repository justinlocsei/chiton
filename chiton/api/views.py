from django.conf import settings
from ipware.ip import get_ip
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chiton.api.permissions import IsRecommender
from chiton.core.schema import DataShapeError
from chiton.wintour.matching import make_recommendations
from chiton.wintour.models import Recommendation
from chiton.wintour.pipelines.core import CorePipeline
from chiton.wintour.profiles import PipelineProfile


class Recommendations(APIView):
    """Manage outfit recommendations."""

    permission_classes = (IsRecommender,)

    def post(self, request, format=None):
        """Generate recommendations for a user."""
        custom_ip = request.data.pop('client_ip_address', None)
        max_garments_per_group = request.data.pop('max_garments_per_group', None)

        try:
            profile = PipelineProfile(request.data, validate=True)
        except DataShapeError as e:
            return Response({'errors': {'fields': e.fields}}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'errors': {'server': str(e)}}, status=status.HTTP_400_BAD_REQUEST)

        ip_address = get_ip(request) if settings.CHITON_API_IS_PUBLIC else custom_ip
        recommendation = Recommendation.objects.create(profile=profile, ip_address=ip_address)

        recommendations = make_recommendations(profile, CorePipeline(), max_garments_per_group=max_garments_per_group)
        recommendations['recommendation_id'] = recommendation.pk
        return Response(recommendations)
