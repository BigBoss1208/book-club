from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db.models import Q, F

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    publish_year = models.IntegerField(validators=[MinValueValidator(1900)])
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to='book_covers/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        null=True,
        blank=True
    )
    total_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    available_copies = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='books')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'books'
        verbose_name = 'Sách'
        verbose_name_plural = 'Sách'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=Q(available_copies__lte=F('total_copies')),
                name='available_not_exceed_total'
            )
        ]

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available_copies > 0 and self.is_active