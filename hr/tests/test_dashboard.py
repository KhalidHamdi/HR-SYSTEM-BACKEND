import pytest
from rest_framework import status
from django.urls import reverse
from hr.factories import AttendanceFactory


@pytest.mark.django_db
class TestDashboard:

    def test_dashboard_access_as_hr_user(self, authenticated_hr_client):
        """dashboard access for HR user."""
        AttendanceFactory.create_batch(5, is_present=True)
        AttendanceFactory.create_batch(2, is_present=False)

        response = authenticated_hr_client.get(reverse('dashboard'))

        assert response.status_code == status.HTTP_200_OK
        assert 'total_employees' in response.data
        assert 'present_today' in response.data
        assert 'absent_today' in response.data

    def test_dashboard_access_as_normal_user(self, authenticated_normal_user_client):
        """dashboard access for normal user (forbidden)."""
        response = authenticated_normal_user_client.get(reverse('dashboard'))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_dashboard_no_attendance_data(self, authenticated_hr_client):
        """dashboard when no attendance data exists."""
        response = authenticated_hr_client.get(reverse('dashboard'))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['present_today'] == 0
        assert response.data['absent_today'] == 0
