from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("student_code", "full_name", "faculty", "class_name", "created_at")
    search_fields = ("student_code", "full_name")
