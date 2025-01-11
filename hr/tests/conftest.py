import pytest
from rest_framework.test import APIClient
from hr.factories import EmployeeFactory


@pytest.fixture
def api_client():
    """providing an API client."""
    return APIClient()


@pytest.fixture
def hr_user(db):
    """creating an HR user."""
    return EmployeeFactory(employee_type='HR')


@pytest.fixture
def normal_user(db):
    """creating a normal user."""
    return EmployeeFactory(employee_type='NORMAL')


@pytest.fixture
def authenticated_hr_client(api_client, hr_user):
    """an authenticated HR user."""
    api_client.force_authenticate(user=hr_user)
    return api_client


@pytest.fixture
def authenticated_normal_user_client(api_client, normal_user):
    """an authenticated normal user."""
    api_client.force_authenticate(user=normal_user)
    return api_client
