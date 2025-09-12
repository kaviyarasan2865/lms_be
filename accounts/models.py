from django.db import models
from django.contrib.auth.models import AbstractUser


# -------------------------------------------------
# 1. USER MODEL (roles: product_owner, college_admin, faculty, student)
# -------------------------------------------------
class User(AbstractUser):
    ROLE_CHOICES = [
        ('product_owner', 'Product Owner'),
        ('college_admin', 'College Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


# -------------------------------------------------
# 2. COLLEGE
# -------------------------------------------------
class College(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=50, unique=True)  # short code for college
    course = models.CharField(max_length=255, default="NEET-PG")  # default course for NEET PG preparation
    address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name


# -------------------------------------------------
# 3. COLLEGE ADMIN
# -------------------------------------------------
class CollegeAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="college_admin_profile")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="admins")

    def __str__(self):
        return f"{self.user.username} - {self.college.name}"


# -------------------------------------------------
# 4. ACADEMIC YEAR
# -------------------------------------------------
class AcademicYear(models.Model):
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name="academic_years")
    year = models.PositiveIntegerField()  # 1, 2, 3, 4
    label = models.CharField(max_length=255, default="Year 1")
    start_date = models.DateField()
    end_date = models.DateField()
    auto_promote = models.BooleanField(default=True)
    editable = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("batch", "year")
        ordering = ['year']

    def __str__(self):
        return f"{self.batch.name} - {self.label}"

# -------------------------------------------------
# 5. BATCH
# -------------------------------------------------
class Batch(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="batches")
    course = models.CharField(max_length=255, default="NEET-PG")  # redundant for quick access

    year_of_joining = models.PositiveIntegerField()
    name = models.CharField(max_length=255)

    # Promotion settings
    auto_promote_after_days = models.PositiveIntegerField(default=365)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("college", "year_of_joining", "name")

    def __str__(self):
        return f"{self.name} ({self.year_of_joining}) - {self.college.name}"


# -------------------------------------------------
# 6. STUDENT
# -------------------------------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="students")
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name="students")

    # personal info
    roll_no = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=255, blank=True, null=True)

    # Academic info
    admission_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_no}"


# -------------------------------------------------
# 7. FACULTY
# -------------------------------------------------
class Faculty(models.Model):
    DESIGNATION_CHOICES = [
        ("assistant_professor", "Assistant Professor"),
        ("professor", "Professor"),
        ("hod", "Head of Department"),
        ("dean", "Dean"),
        ("lecturer", "Lecturer"),
        ("senior_lecturer", "Senior Lecturer"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="faculty_profile")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="faculties")

    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    education_details = models.TextField(blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    specialization = models.CharField(max_length=255, blank=True, null=True)

    # subjects assigned
    subjects = models.ManyToManyField("Subject", blank=True, related_name="faculties")

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.designation}"


# -------------------------------------------------
# 8. SUBJECT (NEET PG subjects)
# -------------------------------------------------
class Subject(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True, null=True)  # Subject code like ANAT001
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("college", "name")

    def __str__(self):
        return self.name


# -------------------------------------------------
# 8. MODULE (Sub-topics within subjects)
# -------------------------------------------------
class Module(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="modules")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1)  # For ordering modules within a subject
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("subject", "name")
        ordering = ["subject", "order"]

    def __str__(self):
        return f"{self.subject.name} - {self.name}"


# -------------------------------------------------
# 9. QUESTION BANK (for future quiz functionality)
# -------------------------------------------------
class QuestionBank(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Easy"),
        ("medium", "Medium"),
        ("hard", "Hard"),
    ]

    QUESTION_TYPE_CHOICES = [
        ("mcq", "Multiple Choice Question"),
        ("true_false", "True/False"),
        ("fill_blank", "Fill in the Blank"),
    ]

    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="question_banks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="questions", null=True, blank=True)
    
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default="mcq")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    
    # For MCQ questions
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    correct_answer = models.CharField(max_length=1, blank=True, null=True)  # A, B, C, D
    
    # Additional content
    explanation = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_questions")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.subject.name} - {self.question_text[:50]}..."


# -------------------------------------------------
# 10. BULK UPLOAD TEMPLATE (for CSV uploads)
# -------------------------------------------------
class BulkUploadTemplate(models.Model):
    TEMPLATE_TYPE_CHOICES = [
        ("student", "Student"),
        ("faculty", "Faculty"),
        ("question", "Question"),
    ]

    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="upload_templates")
    file_path = models.FileField(upload_to="bulk_uploads/")
    status = models.CharField(max_length=20, default="pending")  # pending, processing, completed, failed
    error_log = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.template_type} - {self.college.name}"