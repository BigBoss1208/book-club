from django import forms
from .models import BorrowRequest
from datetime import date, timedelta

class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = ['expected_return_date', 'note']
        widgets = {
            'expected_return_date': forms.DateInput(attrs={'type': 'date', 'min': date.today()}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_expected_return_date(self):
        return_date = self.cleaned_data.get('expected_return_date')
        if return_date and return_date < date.today():
            raise forms.ValidationError('Ngày trả phải từ hôm nay trở đi')
        if return_date and return_date > date.today() + timedelta(days=30):
            raise forms.ValidationError('Thời gian mượn tối đa 30 ngày')
        return return_date