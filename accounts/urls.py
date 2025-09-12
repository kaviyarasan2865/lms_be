from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
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
    
    # Faculty management
    path('faculties/', views.FacultyListCreateView.as_view(), name='faculty-list'),
    path('faculties/<int:pk>/', views.FacultyDetailView.as_view(), name='faculty-detail'),
    
    # Subject management
    path('subjects/', views.SubjectListCreateView.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),
]
