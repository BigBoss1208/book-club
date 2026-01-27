from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from library.models import Book, Category
from borrowing.models import BorrowRequest, BorrowTransaction
from reviews.models import Review


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    # Overall statistics
    total_books = Book.objects.filter(is_active=True).count()
    total_categories = Category.objects.filter(is_active=True).count()
    total_users = User.objects.filter(is_active=True).count()

    # Current borrowing stats
    active_borrows = BorrowTransaction.objects.filter(status__in=['BORROWING', 'OVERDUE']).count()
    overdue_borrows = BorrowTransaction.objects.filter(status='OVERDUE').count()
    pending_requests = BorrowRequest.objects.filter(status='PENDING').count()
    pending_reviews = Review.objects.filter(status='PENDING').count()

    # Top borrowed books
    top_books = Book.objects.annotate(
        borrow_count=Count('borrow_requests', filter=Q(borrow_requests__status='APPROVED'))
    ).order_by('-borrow_count')[:5]

    # Top categories
    top_categories = Category.objects.annotate(
        borrow_count=Count('books__borrow_requests', filter=Q(books__borrow_requests__status='APPROVED'))
    ).order_by('-borrow_count')[:5]

    # Borrow trend (last 30 days)
    today = timezone.now().date()
    borrow_trend = []
    for i in range(30):
        date = today - timedelta(days=29 - i)
        count = BorrowTransaction.objects.filter(
            borrowed_at__date=date
        ).count()
        borrow_trend.append({'date': date.strftime('%d/%m'), 'count': count})

    context = {
        'total_books': total_books,
        'total_categories': total_categories,
        'total_users': total_users,
        'active_borrows': active_borrows,
        'overdue_borrows': overdue_borrows,
        'pending_requests': pending_requests,
        'pending_reviews': pending_reviews,
        'top_books': top_books,
        'top_categories': top_categories,
        'borrow_trend': borrow_trend,
    }
    return render(request, 'dashboard/dashboard.html', context)