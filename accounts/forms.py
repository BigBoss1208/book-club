from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile

class StudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    student_code = forms.CharField(max_length=20)
    full_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    faculty = forms.CharField(max_length=100)
    class_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                student_code=self.cleaned_data['student_code'],
                full_name=self.cleaned_data['full_name'],
                phone=self.cleaned_data['phone'],
                faculty=self.cleaned_data['faculty'],
                class_name=self.cleaned_data['class_name']
            )
        return user