from django.conf import settings
from django.db import models
from apps.library.models import Book

class BorrowRequestStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"

class BorrowRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrow_requests")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="borrow_requests")

    request_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()

    status = models.CharField(max_length=20, choices=BorrowRequestStatus.choices, default=BorrowRequestStatus.PENDING)
    note = models.TextField(blank=True)

    handled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="handled_borrow_requests")
    handled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-request_date"]

    def __str__(self):
        return f"Request#{self.id} - {self.user.username} - {self.book.title} - {self.status}"


class BorrowTransactionStatus(models.TextChoices):
    BORROWING = "BORROWING", "Borrowing"
    RETURN_PENDING = "RETURN_PENDING", "Return pending"
    RETURNED = "RETURNED", "Returned"
    OVERDUE = "OVERDUE", "Overdue"

class BorrowTransaction(models.Model):
    borrow_request = models.OneToOneField(BorrowRequest, on_delete=models.CASCADE, related_name="transaction")
    borrowed_at = models.DateTimeField()
    due_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=BorrowTransactionStatus.choices, default=BorrowTransactionStatus.BORROWING)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]

    def __str__(self):
        return f"TX#{self.id} - Request#{self.borrow_request_id} - {self.status}"
