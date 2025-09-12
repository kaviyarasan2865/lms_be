# LMS Backend - NEET PG Preparation Platform

This is the Django REST API backend for the Learning Management System designed specifically for NEET PG preparation students.

## Features

- **Multi-role Authentication**: Product Owner, College Admin, Faculty, and Student roles
- **JWT Token Authentication**: Secure token-based authentication with refresh tokens
- **College Management**: Complete college administration system
- **Batch Management**: Academic year and promotion settings
- **Student Management**: Comprehensive student profiles with bulk upload
- **Faculty Management**: Faculty profiles with subject assignments
- **Question Bank**: Centralized question management with multimedia support
- **Subject & Module Management**: Organized curriculum structure
- **Analytics**: Dashboard analytics for college administrators

## Tech Stack

- **Django 4.2**: Web framework
- **Django REST Framework**: API development
- **JWT Authentication**: Secure token-based auth
- **MySQL**: Database
- **CORS**: Cross-origin resource sharing
- **Swagger/OpenAPI**: API documentation

## Models Overview

### Core Models

1. **User**: Extended Django user with role-based access
2. **College**: Institution management
3. **CollegeAdmin**: College administrator profiles
4. **Batch**: Academic batches with promotion settings
5. **Student**: Student profiles with personal and academic info
6. **Faculty**: Faculty profiles with subject assignments
7. **Subject**: NEET PG subjects (Anatomy, Physiology, etc.)
8. **Module**: Sub-topics within subjects
9. **QuestionBank**: Questions with multimedia support
10. **BulkUploadTemplate**: CSV upload management

## Setup Instructions

### 1. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Create a MySQL database named `lms_db` and update settings:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lms_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Populate Default Subjects

```bash
python manage.py populate_subjects
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## API Endpoints

### Authentication

- `POST /api/register/` - User registration
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout
- `GET /api/profile/` - User profile

### College Management

- `GET /api/colleges/` - List colleges
- `POST /api/colleges/` - Create college
- `GET /api/colleges/{id}/` - Get college details
- `PUT /api/colleges/{id}/` - Update college
- `DELETE /api/colleges/{id}/` - Delete college

### Batch Management

- `GET /api/batches/` - List batches
- `POST /api/batches/` - Create batch
- `GET /api/batches/{id}/` - Get batch details
- `PUT /api/batches/{id}/` - Update batch
- `DELETE /api/batches/{id}/` - Delete batch

### Student Management

- `GET /api/students/` - List students
- `POST /api/students/register/` - Register student
- `POST /api/students/bulk-upload/` - Bulk upload students
- `GET /api/students/download-template/` - Download CSV template
- `GET /api/students/{id}/` - Get student details
- `PUT /api/students/{id}/` - Update student
- `DELETE /api/students/{id}/` - Delete student

### Faculty Management

- `GET /api/faculties/` - List faculty
- `POST /api/faculties/register/` - Register faculty
- `GET /api/faculties/{id}/` - Get faculty details
- `PUT /api/faculties/{id}/` - Update faculty
- `DELETE /api/faculties/{id}/` - Delete faculty

### Subject Management

- `GET /api/subjects/` - List subjects
- `POST /api/subjects/` - Create subject
- `GET /api/subjects/{id}/` - Get subject details
- `PUT /api/subjects/{id}/` - Update subject
- `DELETE /api/subjects/{id}/` - Delete subject

### Module Management

- `GET /api/modules/` - List modules
- `POST /api/modules/` - Create module
- `GET /api/modules/{id}/` - Get module details
- `PUT /api/modules/{id}/` - Update module
- `DELETE /api/modules/{id}/` - Delete module

### Question Bank

- `GET /api/questions/` - List questions
- `POST /api/questions/` - Create question
- `GET /api/questions/{id}/` - Get question details
- `PUT /api/questions/{id}/` - Update question
- `DELETE /api/questions/{id}/` - Delete question

### Analytics

- `GET /api/analytics/` - College analytics dashboard

## User Roles & Permissions

### Product Owner
- Can manage all colleges
- Full access to all endpoints
- Can view system-wide analytics

### College Admin
- Can manage their college only
- Can create batches, students, faculty
- Can assign subjects to faculty
- Can view college analytics

### Faculty
- Can create and manage questions
- Can view questions for their assigned subjects
- Limited access to other endpoints

### Student
- Can view their profile
- Can access quiz functionality (future feature)
- Limited access to other endpoints

## Default NEET PG Subjects

The system comes pre-populated with standard NEET PG subjects:

- Anatomy
- Physiology
- Biochemistry
- Pathology
- Pharmacology
- Microbiology
- Forensic Medicine
- Community Medicine
- Medicine
- Surgery
- Obstetrics & Gynaecology
- Paediatrics
- Orthopaedics
- Ophthalmology
- ENT
- Dermatology
- Psychiatry
- Anaesthesia
- Radiology
- Emergency Medicine

## Bulk Upload

### Student CSV Template

The system supports bulk upload of students via CSV with the following columns:

- `username` - Student username
- `email` - Student email
- `first_name` - Student first name
- `last_name` - Student last name
- `password` - Student password
- `roll_no` - Student roll number
- `phone_number` - Student phone number
- `date_of_birth` - Student date of birth (YYYY-MM-DD)
- `address` - Student address
- `emergency_contact` - Emergency contact number
- `emergency_contact_name` - Emergency contact name
- `admission_date` - Admission date (YYYY-MM-DD)
- `batch_id` - Batch ID (optional)

## API Documentation

Access Swagger documentation at `http://127.0.0.1:8000/swagger/` when the server is running.

## Environment Variables

Create a `.env` file for production:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=mysql://user:password@host:port/database
```

## Testing

```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper database credentials
3. Set up static file serving
4. Configure CORS for your frontend domain
5. Use environment variables for sensitive data

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure MySQL is running and credentials are correct
2. **CORS Issues**: Check CORS settings for frontend domain
3. **JWT Token Issues**: Verify JWT settings and secret key
4. **Migration Issues**: Check for field conflicts and provide defaults

### Debug Mode

Enable debug logging by setting `DEBUG=True` in settings.py
