from django.contrib.auth.models import User
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from chiton.wintour.models import Person, Recommendation, WardrobeProfile


@pytest.mark.integration
@pytest.mark.django_db
class TestRecommendations:

    ENDPOINT = '/api/wardrobe-profiles/'

    @pytest.fixture
    def api_user(self):
        user = User.objects.create_user('tester')
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

    def test_authorization_token(self, api_user):
        """It requires a user with a valid token."""
        client = APIClient()

        client.credentials(HTTP_AUTHORIZATION='Token %s' % api_user.auth_token.key)
        response = client.post(self.ENDPOINT, {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        client.credentials(HTTP_AUTHORIZATION='Token none')
        response = client.post(self.ENDPOINT, {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile(self, api_client, recommendation_factory):
        """It converts a recommendation to a wardrobe profile."""
        recommendation = recommendation_factory()

        response = api_client.post(self.ENDPOINT, {
            'email': 'test@example.com',
            'recommendation_id': recommendation.pk
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['wardrobe_profile_id'] > 0

        profile = WardrobeProfile.objects.get(pk=response.data['wardrobe_profile_id'])
        assert profile

    def test_profile_person(self, api_client, recommendation_factory):
        """It creates a person for the given email."""
        recommendation = recommendation_factory()

        response = api_client.post(self.ENDPOINT, {
            'email': 'test@example.com',
            'recommendation_id': recommendation.pk
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['wardrobe_profile_id'] > 0

        with_email = [p for p in Person.objects.all() if p.email == 'test@example.com']
        assert len(with_email) == 1

    def test_profile_multiple(self, api_client, recommendation_factory):
        """It allows multiple profiles to be associated with a single email."""
        recommendation_one = recommendation_factory()
        recommendation_two = recommendation_factory()

        response_one = api_client.post(self.ENDPOINT, {
            'email': 'test@example.com',
            'recommendation_id': recommendation_one.pk
        }, format='json')
        assert response_one.status_code == status.HTTP_200_OK

        response_two = api_client.post(self.ENDPOINT, {
            'email': 'test@example.com',
            'recommendation_id': recommendation_two.pk
        }, format='json')
        assert response_one.status_code == status.HTTP_200_OK

        with_email = [p for p in Person.objects.all() if p.email == 'test@example.com']
        assert len(with_email) == 1

        person = with_email[0]
        assert WardrobeProfile.objects.filter(person=person).count() == 2

    def test_profile_errors(self, api_client):
        """It returns errors when given an invalid request."""
        response = api_client.post(self.ENDPOINT, {
            'email': 'invalid'
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'email' in response.data['errors']['fields']


    def test_profile_errors_types(self, api_client):
        """It returns errors when a request contains fields with unexpected types."""
        response = api_client.post(self.ENDPOINT, {
            'recommendation_id': 'one'
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'recommendation_id' in response.data['errors']['fields']

    def test_profile_errors_recommendation(self, api_client):
        """It returns an error when a recommendation ID does not resolve to a recommendation."""
        response = api_client.post(self.ENDPOINT, {
            'email': 'valid@example.com',
            'recommendation_id': 0
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data
        assert 'recommendation' in response.data['errors']
