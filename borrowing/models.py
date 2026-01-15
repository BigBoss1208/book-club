from django.db import models
from django.contrib.auth.models import User
from library.models import Book
from django.utils import timezone

class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Đang chờ'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Từ chối'),
        ('CANCELLED', 'Đã huỷ'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_requests')
    request_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    note = models.TextField(blank=True)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_requests')
    handled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'borrow_requests'
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class BorrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('BORROWING', 'Đang mượn'),
        ('RETURN_PENDING', 'Chờ trả'),
        ('RETURNED', 'Đã trả'),
        ('OVERDUE', 'Quá hạn'),
    ]

    borrow_request = models.OneToOneField(BorrowRequest, on_delete=models.CASCADE, related_name='transaction')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='BORROWING')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_return_days = models.IntegerField(default=0)

    class Meta:
        db_table = 'borrow_transactions'
        ordering = ['-borrowed_at']

    def __str__(self):
        return f"Transaction #{self.id} - {self.borrow_request.user.username}"

    def calculate_fine(self):
        if self.returned_at and self.returned_at > self.due_at:
            days_late = (self.returned_at - self.due_at).days
            self.late_return_days = days_late
            self.fine_amount = days_late * 5000  # 5000 VND/day
            self.save()