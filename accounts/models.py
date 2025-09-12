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
    course = models.CharField(max_length=255)  # default course (e.g., MBBS, NEET-PG)

    created_at = models.DateTimeField(auto_now_add=True)

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
# 4. BATCH
# -------------------------------------------------
class Batch(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="batches")
    course = models.CharField(max_length=255)  # redundant for quick access

    year_of_joining = models.PositiveIntegerField()
    name = models.CharField(max_length=255)

    # Academic phase configuration (4 years default, customizable)
    academic_year = models.PositiveIntegerField(default=1)
    default_label = models.CharField(max_length=255, default="Year 1")
    start_date = models.DateField()
    end_date = models.DateField()
    auto_promote = models.BooleanField(default=True)
    editable = models.BooleanField(default=True)

    # Promotion settings
    auto_promote_after_days = models.PositiveIntegerField(default=365)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("college", "year_of_joining", "name")

    def __str__(self):
        return f"{self.name} ({self.year_of_joining}) - {self.college.name}"


# -------------------------------------------------
# 5. STUDENT
# -------------------------------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="students")
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, related_name="students")

    # personal info
    roll_no = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.roll_no}"


# -------------------------------------------------
# 6. FACULTY
# -------------------------------------------------
class Faculty(models.Model):
    DESIGNATION_CHOICES = [
        ("assistant_professor", "Assistant Professor"),
        ("professor", "Professor"),
        ("hod", "Head of Department"),
        ("dean", "Dean"),
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

    # subjects assigned
    subjects = models.ManyToManyField("Subject", blank=True, related_name="faculties")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.designation}"


# -------------------------------------------------
# 7. SUBJECT (for quick linking to faculties & question bank later)
# -------------------------------------------------
class Subject(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name