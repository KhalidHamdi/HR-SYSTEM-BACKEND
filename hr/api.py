from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from datetime import datetime, timedelta
import csv
from django.http import HttpResponse


def is_hr_employee(user):
    """Check if the user is an HR employee."""
    return user.is_authenticated and user.employee_type == 'HR'


def handle_unauthorized():
    """Return a standard unauthorized response."""
    return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """HR dashboard showing employee statistics and recent activities."""
    if not is_hr_employee(request.user):
        return handle_unauthorized()
    
    today = timezone.now().date()
    total_employees = Employee.objects.count()
    present_today = Attendance.objects.filter(date=today, is_present=True).count()
    absent_today = Attendance.objects.filter(date=today, is_present=False).count()
    
    recent_attendances = Attendance.objects.select_related('employee', 'created_by').order_by('-created_at')[:10]
    activities = [
        {
            'id': attendance.id,
            'type': 'attendance',
            'description': f"{attendance.created_by.username} marked {attendance.employee.username} as {'present' if attendance.is_present else 'absent'}",
            'timestamp': attendance.created_at.isoformat(),
        }
        for attendance in recent_attendances
    ]
    
    return Response({
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'recent_activities': activities,
    })


@api_view(['POST'])
def login_view(request):
    """Login view for HR employees."""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.employee_type != 'HR':
        return Response({'error': 'Access denied. Only HR employees can login.'}, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': EmployeeSerializer(user).data,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def employee_list(request):
    """List all employees or create a new employee."""
    if not is_hr_employee(request.user):
        return handle_unauthorized()
    
    if request.method == 'GET':
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            employee = serializer.save(commit=False)
            employee.set_password(serializer.validated_data['password'])
            employee.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def employee_detail(request, pk):
    """Retrieve, update, or delete an employee."""
    if not is_hr_employee(request.user):
        return handle_unauthorized()
    
    try:
        employee = Employee.objects.get(pk=pk)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def attendance_list(request):
    """List attendances or create a new attendance."""
    if not is_hr_employee(request.user):
        return handle_unauthorized()
    
    if request.method == 'GET':
        date_str = request.query_params.get('date', timezone.now().date())
        period = request.query_params.get('period', 'day')
        export_format = request.query_params.get('export')
        
        try:
            date = datetime.strptime(str(date_str), '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        start_date, end_date = calculate_date_range(date, period)
        
        attendances = Attendance.objects.filter(
            date__range=[start_date, end_date]
        ).select_related('employee', 'created_by').order_by('date', 'employee__first_name')
        
        if export_format == 'csv':
            return export_attendance_to_csv(attendances, period, date)
        
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def attendance_detail(request, pk):
    """Retrieve, update, or delete an attendance record."""
    if not is_hr_employee(request.user):
        return handle_unauthorized()
    
    try:
        attendance = Attendance.objects.get(pk=pk)
    except Attendance.DoesNotExist:
        return Response({'error': 'Attendance not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    if request.method == 'PUT':
        serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def calculate_date_range(date, period):
    """Calculate the date range based on the specified period."""
    if period == 'day':
        return date, date
    if period == 'week':
        start_date = date - timedelta(days=date.weekday())
        end_date = start_date + timedelta(days=6)
    elif period == 'month':
        start_date = date.replace(day=1)
        next_month = date.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
    else:  
        start_date = date.replace(month=1, day=1)
        end_date = date.replace(month=12, day=31)
    return start_date, end_date


def export_attendance_to_csv(attendances, period, date):
    """Export attendance records to a CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{period}_{date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Employee Name', 'Email', 'Status', 'Marked By', 'Marked At'])
    
    for attendance in attendances:
        writer.writerow([
            attendance.date,
            f"{attendance.employee.first_name} {attendance.employee.last_name}",
            attendance.employee.email,
            'Present' if attendance.is_present else 'Absent',
            attendance.created_by.username,
            attendance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    return response
