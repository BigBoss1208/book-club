from django import forms
from .models import Category, Book

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active"]

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            "title","author","publisher","publish_year","isbn",
            "description","cover_image","total_copies","available_copies",
            "category","is_active"
        ]
