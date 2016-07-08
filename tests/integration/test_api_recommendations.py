from django.apps import apps
from django.contrib.auth.management import create_permissions
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from chiton.wintour.apps import Config as Wintour
from chiton.wintour.models import Recommendation, WardrobeProfile


@pytest.mark.integration
@pytest.mark.django_db
class TestRecommendations:

    ENDPOINT = '/api/recommendations/'

    @pytest.fixture(autouse=True)
    def permissions(self):
        app = apps.get_app_config(Wintour.label)
        create_permissions(app, verbosity=0, interactive=False)

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
        Token.objects.create(user=user)

        return User.objects.get(pk=user.pk)

    @pytest.fixture
    def api_client(self, api_user):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token %s' % api_user.auth_token.key)
        return client

    def test_authentication(self):
        """It requires an authenticated user."""
        response = APIClient().post(self.ENDPOINT, {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authorization_token(self, api_user, create_recommendation_permission):
        """It requires a user with recommender permissions and a valid token."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token %s' % api_user.auth_token.key)

        response = client.post(self.ENDPOINT, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        api_user.user_permissions.remove(create_recommendation_permission)
        api_user = User.objects.get(pk=api_user.pk)

        response = client.post(self.ENDPOINT, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_recommendations(self, api_client, formality_factory, standard_size_factory, style_factory):
        """It returns recommendations when given a valid request."""
        formality_factory(slug='casual')
        standard_size_factory(slug='m')
        style_factory(slug='bold-powerful')

        response = api_client.post(self.ENDPOINT, {
            'age': 30,
            'avoid_care': ['dry_clean'],
            'body_shape': 'apple',
            'expectations': [
                {'formality': 'casual', 'frequency': 'always'}
            ],
            'sizes': ['m'],
            'styles': ['bold-powerful']
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'basics' in response.data

    def test_recommendations_errors(self, api_client):
        """It returns errors when given an invalid request."""
        response = api_client.post(self.ENDPOINT, {
            'age': 0
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'age' in response.data['errors']['fields']

    def test_recommendations_errors_types(self, api_client):
        """It returns errors when a request contains fields with unexpected types."""
        response = api_client.post(self.ENDPOINT, {
            'age': 'ten'
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'age' in response.data['errors']['fields']

    def test_recommendations_errors_structures(self, api_client):
        """It returns errors when a request contains fields with unexpected structures."""
        response = api_client.post(self.ENDPOINT, {
            'age': ['10'],
            'avoid_care': [{'value': 'dry_clean'}],
            'body_shape': {'value': 'rectangle'},
            'expectations': 'formal',
            'sizes': 10,
            'styles': {'type': 'classy'}
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'fields' in response.data['errors']
