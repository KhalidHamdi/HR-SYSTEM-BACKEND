import factory
from django.utils.timezone import now
from .models import Employee, Attendance

class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee
        skip_postgeneration_save = True  


    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    employee_type = factory.Faker('random_element', elements=['HR', 'NORMAL'])
    email = factory.Sequence(lambda n: f"user{n}@example.com")

class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendance

    employee = factory.SubFactory(EmployeeFactory)
    date = factory.Faker('date')
    is_present = factory.Faker('boolean')
    created_by = factory.SubFactory(
        EmployeeFactory, 
        employee_type='HR'
    )
