from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, College, CollegeAdmin, Batch, AcademicYear, Student, Faculty, Subject, 
    Module, QuestionBank, BulkUploadTemplate
)


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
        fields = [
            'id', 'name', 'code', 'course', 'address', 'contact_email', 
            'contact_phone', 'created_at', 'updated_at'
        ]


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'year', 'label', 'start_date', 'end_date', 
            'auto_promote', 'editable', 'created_at', 'updated_at'
        ]

class BatchSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    student_count = serializers.SerializerMethodField()
    academic_years = AcademicYearSerializer(many=True, read_only=True)
    
    class Meta:
        model = Batch
        fields = [
            'id', 'college', 'college_name', 'course', 'year_of_joining', 'name',
            'auto_promote_after_days', 'student_count', 'academic_years',
            'created_at', 'updated_at'
        ]
    
    def get_student_count(self, obj):
        return obj.students.count()

class BatchCreateSerializer(serializers.ModelSerializer):
    academic_years = AcademicYearSerializer(many=True, write_only=True)
    
    class Meta:
        model = Batch
        fields = [
            'college', 'course', 'year_of_joining', 'name',
            'auto_promote_after_days', 'academic_years'
        ]
    
    def create(self, validated_data):
        academic_years_data = validated_data.pop('academic_years', [])
        batch = Batch.objects.create(**validated_data)
        
        # Create academic years for the batch
        for year_data in academic_years_data:
            AcademicYear.objects.create(batch=batch, **year_data)
        
        return batch
    
    def update(self, instance, validated_data):
        academic_years_data = validated_data.pop('academic_years', [])
        
        # Update batch fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update academic years if provided
        if academic_years_data:
            # Delete existing academic years
            instance.academic_years.all().delete()
            
            # Create new academic years
            for year_data in academic_years_data:
                AcademicYear.objects.create(batch=instance, **year_data)
        
        return instance


class SubjectSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    module_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'description', 'college', 'college_name', 
            'is_active', 'module_count', 'created_at', 'updated_at'
        ]
    
    def get_module_count(self, obj):
        return obj.modules.count()


class UserNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for User fields in Student"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email', 'first_name', 'last_name']


class StudentSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'college', 'college_name', 'batch', 'batch_name',
            'roll_no', 'phone_number', 'date_of_birth', 'address', 
            'emergency_contact', 'emergency_contact_name', 'admission_date',
            'is_active', 'full_name', 'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else ''


class FacultySerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    subjects_list = SubjectSerializer(source='subjects', many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Faculty
        fields = [
            'id', 'user', 'college', 'college_name', 'designation', 'status',
            'education_details', 'experience_years', 'specialization', 'subjects', 
            'subjects_list', 'full_name', 'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else ''


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


# -------------------------------------------------
# NEW SERIALIZERS FOR ENHANCED FUNCTIONALITY
# -------------------------------------------------

class ModuleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'subject', 'subject_name', 'name', 'description', 'order',
            'is_active', 'question_count', 'created_at', 'updated_at'
        ]
    
    def get_question_count(self, obj):
        return obj.questions.count()


class QuestionBankSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    module_name = serializers.CharField(source='module.name', read_only=True)
    college_name = serializers.CharField(source='college.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = QuestionBank
        fields = [
            'id', 'college', 'college_name', 'subject', 'subject_name', 'module', 'module_name',
            'question_text', 'question_type', 'difficulty', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'explanation', 'video_url', 'image_url', 'created_by', 'created_by_name',
            'is_active', 'created_at', 'updated_at'
        ]


class BulkUploadTemplateSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    
    class Meta:
        model = BulkUploadTemplate
        fields = [
            'id', 'template_type', 'college', 'college_name', 'file_path', 
            'status', 'error_log', 'created_at', 'updated_at'
        ]


# -------------------------------------------------
# STUDENT REGISTRATION SERIALIZER
# -------------------------------------------------
class StudentRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    college_id = serializers.IntegerField(write_only=True)
    batch_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm',
            'college_id', 'batch_id', 'roll_no', 'phone_number', 'date_of_birth', 
            'address', 'emergency_contact', 'emergency_contact_name', 'admission_date'
        ]
    
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
    
    def validate_roll_no(self, value):
        if Student.objects.filter(roll_no=value).exists():
            raise serializers.ValidationError("A student with this roll number already exists.")
        return value
    
    def create(self, validated_data):
        from django.db import transaction
        
        with transaction.atomic():
            # Create user
            user_data = {
                'username': validated_data.pop('username'),
                'email': validated_data.pop('email'),
                'first_name': validated_data.pop('first_name'),
                'last_name': validated_data.pop('last_name'),
                'password': validated_data.pop('password'),
                'role': 'student'
            }
            validated_data.pop('password_confirm')
            
            user = User.objects.create_user(**user_data)
            
            # Create student profile
            college_id = validated_data.pop('college_id')
            batch_id = validated_data.pop('batch_id', None)
            
            college = College.objects.get(id=college_id)
            batch = Batch.objects.get(id=batch_id) if batch_id else None
            
            student = Student.objects.create(
                user=user,
                college=college,
                batch=batch,
                **validated_data
            )
            
        return student


# -------------------------------------------------
# STUDENT UPDATE SERIALIZER
# -------------------------------------------------
class StudentUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    college_id = serializers.IntegerField(write_only=True, required=False)
    batch_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'college_id', 'batch_id', 'roll_no', 'phone_number', 'date_of_birth', 
            'address', 'emergency_contact', 'emergency_contact_name', 'admission_date'
        ]
    
    def validate_email(self, value):
        # Only validate uniqueness if email is being changed
        if value and self.instance and self.instance.user.email != value:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        # Only validate uniqueness if username is being changed
        if value and self.instance and self.instance.user.username != value:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_roll_no(self, value):
        # Only validate uniqueness if roll_no is being changed
        if value and self.instance and self.instance.roll_no != value:
            if Student.objects.filter(roll_no=value).exists():
                raise serializers.ValidationError("A student with this roll number already exists.")
        return value
    
    def update(self, instance, validated_data):
        from django.db import transaction
        
        with transaction.atomic():
            # Update user data
            user_data = {}
            if 'username' in validated_data:
                user_data['username'] = validated_data.pop('username')
            if 'email' in validated_data:
                user_data['email'] = validated_data.pop('email')
            if 'first_name' in validated_data:
                user_data['first_name'] = validated_data.pop('first_name')
            if 'last_name' in validated_data:
                user_data['last_name'] = validated_data.pop('last_name')
            
            if user_data:
                for attr, value in user_data.items():
                    setattr(instance.user, attr, value)
                instance.user.save()
            
            # Update student profile
            if 'college_id' in validated_data:
                college_id = validated_data.pop('college_id')
                instance.college = College.objects.get(id=college_id)
            
            if 'batch_id' in validated_data:
                batch_id = validated_data.pop('batch_id')
                instance.batch = Batch.objects.get(id=batch_id) if batch_id else None
            
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            return instance


# -------------------------------------------------
# FACULTY REGISTRATION SERIALIZER
# -------------------------------------------------
class FacultyRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    college_id = serializers.IntegerField(write_only=True)
    subject_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Faculty
        fields = [
            'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm',
            'college_id', 'designation', 'status', 'education_details', 
            'experience_years', 'specialization', 'subject_ids'
        ]
    
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
        from django.db import transaction
        
        with transaction.atomic():
            # Create user
            user_data = {
                'username': validated_data.pop('username'),
                'email': validated_data.pop('email'),
                'first_name': validated_data.pop('first_name'),
                'last_name': validated_data.pop('last_name'),
                'password': validated_data.pop('password'),
                'role': 'faculty'
            }
            validated_data.pop('password_confirm')
            
            user = User.objects.create_user(**user_data)
            
            # Create faculty profile
            college_id = validated_data.pop('college_id')
            subject_ids = validated_data.pop('subject_ids', [])
            
            college = College.objects.get(id=college_id)
            
            faculty = Faculty.objects.create(
                user=user,
                college=college,
                **validated_data
            )
            
            # Assign subjects
            if subject_ids:
                subjects = Subject.objects.filter(id__in=subject_ids, college=college)
                faculty.subjects.set(subjects)
            
            return faculty
