from django.contrib import admin
from .models import Employee, Attendance
# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
        
admin.site.register(Employee)
admin.site.register(Attendance)