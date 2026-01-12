from django.contrib import admin
from .models import BorrowRequest, BorrowTransaction

@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "status", "request_date", "expected_return_date", "handled_by")
    list_filter = ("status", "book")
    search_fields = ("user__username", "book__title")

@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "borrow_request", "status", "borrowed_at", "due_at", "returned_at", "fine_amount")
    list_filter = ("status",)
