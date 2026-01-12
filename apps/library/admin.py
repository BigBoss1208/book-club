from django.contrib import admin
from .models import Category, Book

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "available_copies", "is_active", "created_at")
    search_fields = ("title", "author", "isbn")
    list_filter = ("category", "is_active")
