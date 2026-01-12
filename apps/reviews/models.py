from django.conf import settings
from django.db import models
from apps.library.models import Book
from apps.borrowing.models import BorrowTransaction

class ReviewStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="reviews")

    # nullable hoặc required tùy bạn; ở thiết kế Skill 1 cho phép nullable
    borrow_transaction = models.OneToOneField(BorrowTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="review")

    rating = models.PositiveSmallIntegerField()
    content = models.TextField()

    status = models.CharField(max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="moderated_reviews")
    moderated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review#{self.id} - {self.book.title} - {self.status}"
