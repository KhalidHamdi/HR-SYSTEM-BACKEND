import pytest
from rest_framework import status
from django.urls import reverse


@pytest.mark.django_db
class TestLogin:
    def test_successful_login(self, api_client, hr_user):
        """login with valid credentials."""
        hr_user.set_password('password123')
        hr_user.save()

        response = api_client.post(reverse('login'), {
            'username': hr_user.username,
            'password': 'password123',
        })

        assert response.status_code == status.HTTP_200_OK

    def test_login_with_invalid_credentials(self, api_client, hr_user):
        """login with invalid credentials."""
        response = api_client.post(reverse('login'), {
            'username': hr_user.username,
            'password': 'wrongpassword',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_normal_user_login(self, api_client, normal_user):
        """login with a normal user (fail with 403)."""
        normal_user.set_password('password123')
        normal_user.save()

        response = api_client.post(reverse('login'), {
            'username': normal_user.username,
            'password': 'password123', 
        })

        assert response.status_code == status.HTTP_403_FORBIDDEN
