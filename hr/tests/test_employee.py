import pytest
from rest_framework import status
from django.urls import reverse
from hr.models import Employee
from hr.factories import EmployeeFactory


@pytest.mark.django_db
class TestEmployeeAPI:
    def test_get_employee_list(self, authenticated_hr_client):
        """HR can retrieve the list of employees."""
        Employee.objects.all().delete()
        EmployeeFactory.create_batch(5)

        response = authenticated_hr_client.get(reverse('employee-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 5

    def test_create_employee(self, authenticated_hr_client):
        """HR can create a new employee."""
        response = authenticated_hr_client.post(reverse('employee-list'), {
            'username': 'newuser',
            'password': 'password123',
            'email': 'newuser@gmail.com',
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@gmail.com'

    def test_create_employee_missing_fields(self, authenticated_hr_client):
        """creating an employee fails if required fields are missing."""
        response = authenticated_hr_client.post(reverse('employee-list'), {
            'password': 'password123',
            'email': 'newuser@gmail.com',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

        response = authenticated_hr_client.post(reverse('employee-list'), {
            'username': 'newuser',
            'password': 'password123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_create_employee_invalid_email(self, authenticated_hr_client):
        """creating an employee with an invalid email returns an error."""
        response = authenticated_hr_client.post(reverse('employee-list'), {
            'username': 'newuser',
            'password': 'password123',
            'email': 'invalid-email',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_get_employee_list_no_employees(self, authenticated_hr_client):
        """HR gets an empty list when no employees exist."""
        Employee.objects.all().delete()

        response = authenticated_hr_client.get(reverse('employee-list'))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_update_employee(self, authenticated_hr_client):
        """HR can update an existing employee's information."""
        employee = EmployeeFactory()

        response = authenticated_hr_client.put(
            reverse('employee-detail', args=[employee.id]), {
                'username': 'updateduser',
                'email': 'updated@gmail.com',
                'password': 'newpassword123',
            })

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'updateduser'
        assert response.data['email'] == 'updated@gmail.com'

    def test_update_employee_invalid_data(self, authenticated_hr_client):
        """HR cannot update an employee with invalid data."""
        employee = EmployeeFactory()

        response = authenticated_hr_client.put(
            reverse('employee-detail', args=[employee.id]), {
                'username': 'updateduser',
                'email': 'invalid-email',
                'password': 'newpassword123',
            })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_delete_employee(self, authenticated_hr_client):
        """HR can delete an employee."""
        employee = EmployeeFactory()

        response = authenticated_hr_client.delete(reverse('employee-detail', args=[employee.id]))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Employee.objects.filter(id=employee.id).count() == 0

    def test_delete_employee_not_found(self, authenticated_hr_client):
        """attempting to delete a non-existent employee returns an error."""
        response = authenticated_hr_client.delete(reverse('employee-detail', args=[999]))

        assert response.status_code == status.HTTP_404_NOT_FOUND
