from django.conf import settings
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publish_year = models.IntegerField(null=True, blank=True)
    isbn = models.CharField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)

    cover_image = models.ImageField(upload_to="books/covers/", null=True, blank=True)

    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
