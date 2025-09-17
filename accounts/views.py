from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate
from django.db import transaction
from django.http import HttpResponse
import csv
import io
from .models import (
    User, College, CollegeAdmin, Batch, AcademicYear, Student, Faculty, Subject, 
    Module, QuestionBank, BulkUploadTemplate
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    CollegeSerializer, BatchSerializer, BatchCreateSerializer, AcademicYearSerializer,
    StudentSerializer, StudentUpdateSerializer, FacultySerializer, SubjectSerializer,
    ModuleSerializer, QuestionBankSerializer, BulkUploadTemplateSerializer,
    StudentRegistrationSerializer, FacultyRegistrationSerializer, FacultyUpdateSerializer
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register a new user
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                user = serializer.save()
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                return Response({
                    'message': 'User registered successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                    },
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'Registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """
    Login user and return JWT tokens
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
            },
            'tokens': {
                'access': str(access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid credentials',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """
    Get current user profile
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_user(request):
    """
    Logout user (invalidate token)
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        # Even if token blacklisting fails, we should still return success
        # as the client has already cleared the tokens
        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)


# College Management Views
class CollegeListCreateView(generics.ListCreateAPIView):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only product owners can see all colleges
        if self.request.user.role == 'product_owner':
            return College.objects.all()
        # College admins can only see their own college
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return College.objects.filter(id=self.request.user.college_admin_profile.college.id)
        return College.objects.none()


class CollegeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = College.objects.all()
    serializer_class = CollegeSerializer
    permission_classes = [permissions.IsAuthenticated]


# Batch Management Views
class BatchListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BatchCreateSerializer
        return BatchSerializer

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Batch.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Batch.objects.filter(college=self.request.user.college_admin_profile.college)
        return Batch.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            serializer.save(college=self.request.user.college_admin_profile.college)


class BatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BatchCreateSerializer
        return BatchSerializer

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Batch.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Batch.objects.filter(college=self.request.user.college_admin_profile.college)
        return Batch.objects.none()


# Student Management Views
class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Student.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Student.objects.filter(college=self.request.user.college_admin_profile.college)
        return Student.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            serializer.save(college=self.request.user.college_admin_profile.college)


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return StudentUpdateSerializer
        return StudentSerializer

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Student.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Student.objects.filter(college=self.request.user.college_admin_profile.college)
        return Student.objects.none()
    
    def perform_destroy(self, instance):
        """Custom delete to properly handle user and student deletion"""
        try:
            with transaction.atomic():
                # Get the user before deleting the student
                user = instance.user
                # Delete the student first
                instance.delete()
                # Then delete the associated user
                if user:
                    user.delete()
        except Exception as e:
            raise Exception(f"Failed to delete student: {str(e)}")


# Faculty Management Views
class FacultyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FacultyRegistrationSerializer
        return FacultySerializer

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Faculty.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Faculty.objects.filter(college=self.request.user.college_admin_profile.college)
        return Faculty.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            # The FacultyRegistrationSerializer will get college_id from context
            serializer.save()
        else:
            raise PermissionError("Only college admins can create faculty")


class FacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return FacultyUpdateSerializer
        return FacultySerializer

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Faculty.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Faculty.objects.filter(college=self.request.user.college_admin_profile.college)
        return Faculty.objects.none()
    
    def perform_destroy(self, instance):
        """Custom delete to properly handle user and faculty deletion"""
        try:
            with transaction.atomic():
                # Get the user before deleting the faculty
                user = instance.user
                # Delete the faculty first
                instance.delete()
                # Then delete the associated user
                if user:
                    user.delete()
        except Exception as e:
            raise Exception(f"Failed to delete faculty: {str(e)}")


# Subject Management Views
class SubjectListCreateView(generics.ListCreateAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Subject.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Subject.objects.filter(college=self.request.user.college_admin_profile.college)
        return Subject.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            serializer.save(college=self.request.user.college_admin_profile.college)


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Subject.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Subject.objects.filter(college=self.request.user.college_admin_profile.college)
        return Subject.objects.none()


# -------------------------------------------------
# NEW VIEWS FOR ENHANCED FUNCTIONALITY
# -------------------------------------------------

# Module Management Views
class ModuleListCreateView(generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            return Module.objects.filter(subject_id=subject_id)
        
        if self.request.user.role == 'product_owner':
            return Module.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Module.objects.filter(subject__college=self.request.user.college_admin_profile.college)
        return Module.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            college = self.request.user.college_admin_profile.college
            subject = serializer.validated_data.get('subject')
            if subject.college != college:
                raise serializers.ValidationError("Subject must belong to your college.")
        serializer.save()


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Module.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Module.objects.filter(subject__college=self.request.user.college_admin_profile.college)
        return Module.objects.none()


# Question Bank Management Views
class QuestionBankListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionBankSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return QuestionBank.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return QuestionBank.objects.filter(college=self.request.user.college_admin_profile.college)
        elif self.request.user.role == 'faculty' and hasattr(self.request.user, 'faculty_profile'):
            return QuestionBank.objects.filter(college=self.request.user.faculty_profile.college)
        return QuestionBank.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            serializer.save(college=self.request.user.college_admin_profile.college, created_by=self.request.user)
        elif self.request.user.role == 'faculty' and hasattr(self.request.user, 'faculty_profile'):
            serializer.save(college=self.request.user.faculty_profile.college, created_by=self.request.user)


class QuestionBankDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionBankSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return QuestionBank.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return QuestionBank.objects.filter(college=self.request.user.college_admin_profile.college)
        elif self.request.user.role == 'faculty' and hasattr(self.request.user, 'faculty_profile'):
            return QuestionBank.objects.filter(college=self.request.user.faculty_profile.college)
        return QuestionBank.objects.none()


# Student Registration View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_student(request):
    """
    Register a new student (only college admins can do this)
    """
    if request.user.role != 'college_admin':
        return Response({
            'error': 'Only college admins can register students'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = StudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                student = serializer.save()
                
                return Response({
                    'message': 'Student registered successfully',
                    'student': StudentSerializer(student).data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'Student registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Faculty Registration View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def register_faculty(request):
    """
    Register a new faculty member (only college admins can do this)
    """
    if request.user.role != 'college_admin':
        return Response({
            'error': 'Only college admins can register faculty'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = FacultyRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                faculty = serializer.save()
                
                return Response({
                    'message': 'Faculty registered successfully',
                    'faculty': FacultySerializer(faculty).data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'error': 'Faculty registration failed',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Bulk Upload Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_upload_students(request):
    """
    Bulk upload students from CSV file
    """
    if request.user.role != 'college_admin':
        return Response({
            'error': 'Only college admins can bulk upload students'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if 'file' not in request.FILES:
        return Response({
            'error': 'No file provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    if not file.name.endswith('.csv'):
        return Response({
            'error': 'File must be a CSV file'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Read CSV file
        decoded_file = file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(decoded_file))
        
        college = request.user.college_admin_profile.college
        created_students = []
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(csv_data, start=2):  # Start from 2 because of header
                try:
                    # Create user
                    user = User.objects.create_user(
                        username=row['username'],
                        email=row['email'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        password=row['password'],
                        role='student'
                    )
                    
                    # Get batch if provided
                    batch = None
                    if row.get('batch_id'):
                        batch = Batch.objects.get(id=row['batch_id'], college=college)
                    
                    # Create student
                    student = Student.objects.create(
                        user=user,
                        college=college,
                        batch=batch,
                        roll_no=row['roll_no'],
                        phone_number=row.get('phone_number', ''),
                        date_of_birth=row.get('date_of_birth'),
                        address=row.get('address', ''),
                        emergency_contact=row.get('emergency_contact', ''),
                        emergency_contact_name=row.get('emergency_contact_name', ''),
                        admission_date=row.get('admission_date')
                    )
                    
                    created_students.append(StudentSerializer(student).data)
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
        
        return Response({
            'message': f'Successfully created {len(created_students)} students',
            'created_students': created_students,
            'errors': errors
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': 'Bulk upload failed',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_student_template(request):
    """
    Download CSV template for student bulk upload
    """
    if request.user.role != 'college_admin':
        return Response({
            'error': 'Only college admins can download templates'
        }, status=status.HTTP_403_FORBIDDEN)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'username', 'email', 'first_name', 'last_name', 'password', 
        'roll_no', 'phone_number', 'date_of_birth', 'address', 
        'emergency_contact', 'emergency_contact_name', 'admission_date', 'batch_id'
    ])
    
    return response


# Analytics Views
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def college_analytics(request):
    """
    Get analytics for college admin dashboard
    """
    if request.user.role != 'college_admin':
        return Response({
            'error': 'Only college admins can access analytics'
        }, status=status.HTTP_403_FORBIDDEN)
    
    college = request.user.college_admin_profile.college
    
    analytics = {
        'total_students': Student.objects.filter(college=college).count(),
        'total_faculty': Faculty.objects.filter(college=college).count(),
        'total_batches': Batch.objects.filter(college=college).count(),
        'total_subjects': Subject.objects.filter(college=college).count(),
        'total_questions': QuestionBank.objects.filter(college=college).count(),
        'active_students': Student.objects.filter(college=college, is_active=True).count(),
        'active_faculty': Faculty.objects.filter(college=college, status='active').count(),
    }
    
    return Response(analytics, status=status.HTTP_200_OK)