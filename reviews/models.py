from django.db import models
from django.contrib.auth.models import User
from library.models import Book
from borrowing.models import BorrowTransaction
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Đang chờ duyệt'),
        ('APPROVED', 'Đã duyệt'),
        ('REJECTED', 'Từ chối'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    borrow_transaction = models.ForeignKey(
        BorrowTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_reviews'
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = [['user', 'book']]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}★)"