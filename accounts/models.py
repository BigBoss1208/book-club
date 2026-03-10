from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    student_code = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^[A-Z0-9]+$', 'Mã sinh viên chỉ chứa chữ in hoa và số')]
    )
    full_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Số điện thoại không hợp lệ')]
    )
    faculty = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Hồ sơ sinh viên'
        verbose_name_plural = 'Hồ sơ sinh viên'

    def __str__(self):
        return f"{self.student_code} - {self.full_name}"