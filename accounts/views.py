from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, College, CollegeAdmin, Batch, Student, Faculty, Subject
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    CollegeSerializer, BatchSerializer, StudentSerializer, FacultySerializer, SubjectSerializer
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
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    serializer_class = BatchSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Student.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Student.objects.filter(college=self.request.user.college_admin_profile.college)
        return Student.objects.none()


# Faculty Management Views
class FacultyListCreateView(generics.ListCreateAPIView):
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Faculty.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Faculty.objects.filter(college=self.request.user.college_admin_profile.college)
        return Faculty.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            serializer.save(college=self.request.user.college_admin_profile.college)


class FacultyDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'product_owner':
            return Faculty.objects.all()
        elif self.request.user.role == 'college_admin' and hasattr(self.request.user, 'college_admin_profile'):
            return Faculty.objects.filter(college=self.request.user.college_admin_profile.college)
        return Faculty.objects.none()


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