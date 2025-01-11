# HR-SYSTEM-BACKEND

## Overview

HR System backend built with Django and Django REST Framework, providing a robust API for employee management and attendance tracking.

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Authentication

The system uses JWT (JSON Web Tokens) for authentication. Only HR employees can access the system.

## Unit Testing

Pytest is used for unit testing to ensure code quality and functionality. To run the unit tests, follow these steps:

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt

2. Run the tests:
   ```bash
    pytest

## Database
The system uses Neon PostgreSQL as the database


## Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Create superuser:
```bash
python manage.py createsuperuser
```

5. Start development server:
```bash
python manage.py runserver
```
