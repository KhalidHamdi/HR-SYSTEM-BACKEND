import pytest
from django.utils import timezone  
from rest_framework import status
from django.urls import reverse
from hr.factories import AttendanceFactory, EmployeeFactory


@pytest.mark.django_db
class TestAttendanceList:
    def test_hr_can_get_attendance_list(self, authenticated_hr_client):
        """HR user can retrieve the attendance list."""
        today = timezone.now().date()
        AttendanceFactory.create_batch(3, date=today)
        response = authenticated_hr_client.get(reverse('attendance-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_normal_user_cannot_get_attendance_list(self, authenticated_normal_user_client):
        """Normal user cannot retrieve the attendance list."""
        response = authenticated_normal_user_client.get(reverse('attendance-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAttendanceCreate:
    def test_hr_can_create_attendance(self, authenticated_hr_client):
        """HR user can create an attendance record."""
        employee = EmployeeFactory()
        attendance_data = {'employee': employee.id, 'date': timezone.now().date(), 'is_present': True}
        response = authenticated_hr_client.post(reverse('attendance-list'), attendance_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['employee'] == employee.id

    @pytest.mark.parametrize('invalid_data', [
        {'employee': 9999, 'date': 'invalid-date', 'is_present': 'not-a-boolean'},
        {'employee': '', 'date': '', 'is_present': ''},
        {'date': timezone.now().date(), 'is_present': True},
    ])
    def test_invalid_data_returns_400(self, authenticated_hr_client, invalid_data):
        """Invalid data returns a 400 Bad Request error."""
        response = authenticated_hr_client.post(reverse('attendance-list'), invalid_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAttendanceUpdate:
    def test_hr_can_update_attendance(self, authenticated_hr_client):
        """HR user can update an attendance record."""
        attendance = AttendanceFactory(is_present=False)
        response = authenticated_hr_client.put(reverse('attendance-detail', args=[attendance.id]), {'is_present': True})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_present'] is True

    def test_normal_user_cannot_update_attendance(self, authenticated_normal_user_client):
        """Normal user cannot update attendance."""
        attendance = AttendanceFactory()
        response = authenticated_normal_user_client.put(reverse('attendance-detail', args=[attendance.id]), {'is_present': True})
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAttendanceDelete:
    def test_hr_can_delete_attendance(self, authenticated_hr_client):
        """HR user can delete an attendance record."""
        attendance = AttendanceFactory()
        response = authenticated_hr_client.delete(reverse('attendance-detail', args=[attendance.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_normal_user_cannot_delete_attendance(self, authenticated_normal_user_client):
        """Normal user cannot delete attendance."""
        attendance = AttendanceFactory()
        response = authenticated_normal_user_client.delete(reverse('attendance-detail', args=[attendance.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN
