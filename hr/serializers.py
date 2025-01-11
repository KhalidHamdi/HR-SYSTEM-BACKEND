from rest_framework import serializers
from .models import Employee, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'username', 'email', 'password', 'employee_type', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        employee_type = validated_data.get('employee_type', 'HR')  
        instance = self.Meta.model(**validated_data)
        if password:
            instance.set_password(password)
        instance.employee_type = employee_type
        instance.save()
        return instance
    

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'date', 'is_present', 
                 'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by']