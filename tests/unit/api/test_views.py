from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
import mock
import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from chiton.api.views import Recommendations
from chiton.core.schema import DataShapeError
from chiton.wintour.apps import Config as Wintour
from chiton.wintour.models import Recommendation, WardrobeProfile
from chiton.wintour.pipelines.core import CorePipeline


MAKE_RECOMMENDATIONS_PATH = 'chiton.api.views.make_recommendations'
PIPELINE_PROFILE_PATH = 'chiton.api.views.PipelineProfile'


@pytest.mark.django_db
class TestRecommendations:

    ENDPOINT = '/api/recommendations/'

    @pytest.fixture(autouse=True)
    def permissions(self):
        app = apps.get_app_config(Wintour.label)
        create_permissions(app, verbosity=0, interactive=False)

    @pytest.fixture
    def send(self):
        return APIRequestFactory()

    @pytest.fixture
    def view(self):
        return Recommendations.as_view()

    @pytest.fixture
    def create_recommendation_permission(self):
        content_type = ContentType.objects.get_for_model(Recommendation)
        return Permission.objects.get(content_type=content_type, codename__startswith='add_')

    @pytest.fixture
    def create_wardrobe_profile_permission(self):
        content_type = ContentType.objects.get_for_model(WardrobeProfile)
        return Permission.objects.get(content_type=content_type, codename__startswith='add_')

    @pytest.fixture
    def api_user(self, create_recommendation_permission, create_wardrobe_profile_permission):
        user = User.objects.create_user('tester')
        user.user_permissions.add(create_recommendation_permission, create_wardrobe_profile_permission)
        return User.objects.get(pk=user.pk)

    @pytest.fixture
    def make_request(self, view, send, api_user):
        def request_fn(payload={}):
            request = send.post(self.ENDPOINT, payload, format='json')
            force_authenticate(request, user=api_user)
            return view(request)

        return request_fn

    def test_authentication(self, view, send):
        """It requires authentication."""
        request = send.post(self.ENDPOINT, {}, format='json')
        response = view(request)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authorization(self, view, send):
        """It denies access to non-API users."""
        request = send.post(self.ENDPOINT, {}, format='json')
        force_authenticate(request, user=User.objects.create_user('tester'))

        response = view(request)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_authorization_permissions(self, view, send, api_user, create_wardrobe_profile_permission):
        """It grants access to users that can create models used for recommendations."""
        request = send.post(self.ENDPOINT, {}, format='json')
        force_authenticate(request, user=api_user)
        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        api_user.user_permissions.remove(create_wardrobe_profile_permission)
        api_user = User.objects.get(pk=api_user.pk)

        request = send.post(self.ENDPOINT, {}, format='json')
        force_authenticate(request, user=api_user)
        response = view(request)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_recommendations(self, make_request):
        """It returns recommendations."""
        with mock.patch(PIPELINE_PROFILE_PATH) as PipelineProfile:
            PipelineProfile.return_value = {'pipeline': 'data'}

            with mock.patch(MAKE_RECOMMENDATIONS_PATH) as make_recommendations:
                make_recommendations.return_value = {'recommendation': 'data'}
                response = make_request({'request': 'body'})

                PipelineProfile.assert_called_with({'request': 'body'}, validate=True)
                assert make_recommendations.call_args[0][0] == {'pipeline': 'data'}
                assert isinstance(make_recommendations.call_args[0][1], CorePipeline)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {'recommendation': 'data'}

    def test_recommendations_limit(self, make_request):
        """It returns a subset of recommendations when limiting the maximum number of garments per facet group."""
        with mock.patch(PIPELINE_PROFILE_PATH) as PipelineProfile:
            PipelineProfile.return_value = {'pipeline': 'data'}

            with mock.patch(MAKE_RECOMMENDATIONS_PATH) as make_recommendations:
                make_recommendations.return_value = {'recommendation': 'data'}
                response = make_request({
                    'max_garments_per_group': 2,
                    'request': 'body'
                })

                PipelineProfile.assert_called_with({'request': 'body'}, validate=True)
                assert make_recommendations.call_args[0][0] == {'pipeline': 'data'}
                assert isinstance(make_recommendations.call_args[0][1], CorePipeline)
                assert make_recommendations.call_args[1]['max_garments_per_group'] == 2


        assert response.status_code == status.HTTP_200_OK

    def test_recommendations_errors(self, make_request):
        """It returns field errors if the request is invalid."""
        with mock.patch(PIPELINE_PROFILE_PATH) as PipelineProfile:
            PipelineProfile.side_effect = DataShapeError('Invalid', fields={
                'one': 'error',
                'two': 'invalid'
            })

            response = make_request({'request': 'body'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            'errors': {
                'fields': {
                    'one': 'error',
                    'two': 'invalid'
                }
            }
        }

    def test_recommendations_errors_fatal(self, make_request):
        """It returns general errors when a non-field error occurs."""
        with mock.patch(PIPELINE_PROFILE_PATH) as PipelineProfile:
            PipelineProfile.side_effect = ValueError('Invalid')
            response = make_request({'request': 'body'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            'errors': {
                'server': 'Invalid'
            }
        }
