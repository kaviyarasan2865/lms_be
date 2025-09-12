from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, College, CollegeAdmin, Batch, Student, Faculty, Subject


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    college_name = serializers.CharField(write_only=True, required=False)
    college_code = serializers.CharField(write_only=True, required=False)
    course = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'password', 
            'password_confirm', 'phone_number', 'role', 'college_name', 
            'college_code', 'course'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        # Remove password_confirm and college-related fields from validated_data
        validated_data.pop('password_confirm')
        college_name = validated_data.pop('college_name', None)
        college_code = validated_data.pop('college_code', None)
        course = validated_data.pop('course', None)

        # Create user
        user = User.objects.create_user(**validated_data)

        # Handle college admin creation
        if user.role == 'college_admin' and college_name and college_code and course:
            college, created = College.objects.get_or_create(
                code=college_code,
                defaults={
                    'name': college_name,
                    'course': course
                }
            )
            CollegeAdmin.objects.create(user=user, college=college)

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password.')


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['id', 'name', 'code', 'course', 'created_at']


class BatchSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    
    class Meta:
        model = Batch
        fields = [
            'id', 'college', 'college_name', 'course', 'year_of_joining', 'name',
            'academic_year', 'default_label', 'start_date', 'end_date',
            'auto_promote', 'editable', 'auto_promote_after_days', 'created_at'
        ]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'college']


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'college', 'college_name', 'batch', 'batch_name',
            'roll_no', 'phone_number'
        ]


class FacultySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    subjects_list = SubjectSerializer(source='subjects', many=True, read_only=True)
    
    class Meta:
        model = Faculty
        fields = [
            'id', 'user', 'college', 'college_name', 'designation', 'status',
            'education_details', 'subjects', 'subjects_list'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    college_admin_profile = serializers.SerializerMethodField()
    student_profile = serializers.SerializerMethodField()
    faculty_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone_number',
            'role', 'is_active', 'date_joined', 'college_admin_profile',
            'student_profile', 'faculty_profile'
        ]

    def get_college_admin_profile(self, obj):
        if hasattr(obj, 'college_admin_profile'):
            return CollegeSerializer(obj.college_admin_profile.college).data
        return None

    def get_student_profile(self, obj):
        if hasattr(obj, 'student_profile'):
            return StudentSerializer(obj.student_profile).data
        return None

    def get_faculty_profile(self, obj):
        if hasattr(obj, 'faculty_profile'):
            return FacultySerializer(obj.faculty_profile).data
        return None
