from django.urls import path
from . import api

urlpatterns = [
    path('login/', api.login_view, name='login'),
    path('dashboard/', api.dashboard, name='dashboard'),
    path('employees/', api.employee_list, name='employee-list'),
    path('employees/<int:pk>/', api.employee_detail, name='employee-detail'),
    path('attendance/', api.attendance_list, name='attendance-list'),
    path('attendance/<int:pk>/', api.attendance_detail, name='attendance-detail'),

]