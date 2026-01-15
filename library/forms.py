from django import forms
from .models import Book, Category
from django.core.exceptions import ValidationError

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'publisher', 'publish_year', 'isbn',
                  'description', 'cover_image', 'total_copies', 'available_copies',
                  'category', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'publish_year': forms.NumberInput(attrs={'min': 1900, 'max': 2025}),
        }

    def clean_cover_image(self):
        image = self.cleaned_data.get('cover_image')
        if image:
            if image.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError('Ảnh không được vượt quá 2MB')
            if not image.content_type in ['image/jpeg', 'image/png', 'image/webp']:
                raise ValidationError('Chỉ chấp nhận file JPG, PNG, WEBP')
        return image

    def clean(self):
        cleaned_data = super().clean()
        total = cleaned_data.get('total_copies')
        available = cleaned_data.get('available_copies')
        if available and total and available > total:
            raise ValidationError('Số lượng khả dụng không được vượt quá tổng số')
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']