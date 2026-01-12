from django.conf import settings
from django.db import models

class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="student_profile"
    )
    student_code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    faculty = models.CharField(max_length=120, blank=True)
    class_name = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"