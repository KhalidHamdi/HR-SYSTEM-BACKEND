# Generated by Django 5.0.2 on 2025-01-10 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hr', '0003_rename_can_manage_hr_employee_can_hire_hr_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='can_hire_hr',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='password_changed',
        ),
        migrations.AddField(
            model_name='employee',
            name='is_password_reset_required',
            field=models.BooleanField(default=True),
        ),
    ]
