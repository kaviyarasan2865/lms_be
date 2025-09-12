from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    
    # College management
    path('colleges/', views.CollegeListCreateView.as_view(), name='college-list'),
    path('colleges/<int:pk>/', views.CollegeDetailView.as_view(), name='college-detail'),
    
    # Batch management
    path('batches/', views.BatchListCreateView.as_view(), name='batch-list'),
    path('batches/<int:pk>/', views.BatchDetailView.as_view(), name='batch-detail'),
    
    # Student management
    path('students/', views.StudentListCreateView.as_view(), name='student-list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/register/', views.register_student, name='register-student'),
    path('students/bulk-upload/', views.bulk_upload_students, name='bulk-upload-students'),
    path('students/download-template/', views.download_student_template, name='download-student-template'),
    
    # Faculty management
    path('faculties/', views.FacultyListCreateView.as_view(), name='faculty-list'),
    path('faculties/<int:pk>/', views.FacultyDetailView.as_view(), name='faculty-detail'),
    path('faculties/register/', views.register_faculty, name='register-faculty'),
    
    # Subject management
    path('subjects/', views.SubjectListCreateView.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),
    
    # Module management
    path('modules/', views.ModuleListCreateView.as_view(), name='module-list'),
    path('modules/<int:pk>/', views.ModuleDetailView.as_view(), name='module-detail'),
    
    # Question Bank management
    path('questions/', views.QuestionBankListCreateView.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionBankDetailView.as_view(), name='question-detail'),
    
    # Analytics
    path('analytics/', views.college_analytics, name='college-analytics'),
]
