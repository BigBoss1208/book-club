from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from apps.library.models import Book, Category
from apps.borrowing.models import BorrowRequest, BorrowRequestStatus

def home(request):
    q = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()

    books = Book.objects.filter(is_active=True)
    if q:
        # Skill 2 đơn giản; Skill 3 sẽ tối ưu Q() + pagination
        books = books.filter(title__icontains=q) | books.filter(author__icontains=q)

    if category_id.isdigit():
        books = books.filter(category_id=int(category_id))

    categories = Category.objects.filter(is_active=True)
    return render(request, "home.html", {"books": books, "categories": categories, "q": q, "category_id": category_id})

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def dashboard(request):
    total_books = Book.objects.count()
    total_requests = BorrowRequest.objects.count()
    pending_requests = BorrowRequest.objects.filter(status=BorrowRequestStatus.PENDING).count()

    return render(request, "dashboard.html", {
        "total_books": total_books,
        "total_requests": total_requests,
        "pending_requests": pending_requests
    })
