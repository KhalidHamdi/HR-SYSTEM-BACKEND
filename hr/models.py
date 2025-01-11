from django.contrib.auth.models import AbstractUser
from django.db import models

class Employee(AbstractUser):
    EMPLOYEE_TYPES = (
        ('HR', 'HR'),
        ('NORMAL', 'Normal Employee'),
    )
    
    employee_type = models.CharField(max_length=10, choices=EMPLOYEE_TYPES, default='NORMAL')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_employee_type_display()})"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='created_attendances')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.username} - {self.date}"