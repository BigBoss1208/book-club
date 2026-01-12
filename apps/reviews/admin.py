from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "rating", "status", "created_at", "moderated_by")
    list_filter = ("status", "rating")
    search_fields = ("book__title", "user__username")
