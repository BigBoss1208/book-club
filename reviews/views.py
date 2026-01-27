from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Review
from .forms import ReviewForm
from library.models import Book
from borrowing.models import BorrowTransaction


@login_required
def create_review_view(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    # Check if user has returned this book
    has_returned = BorrowTransaction.objects.filter(
        borrow_request__user=request.user,
        borrow_request__book=book,
        status='RETURNED'
    ).exists()

    if not has_returned:
        messages.error(request, 'Bạn cần mượn và trả sách này trước khi đánh giá')
        return redirect('library:book_detail', pk=book_id)

    # Check if already reviewed
    if Review.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, 'Bạn đã đánh giá sách này rồi')
        return redirect('library:book_detail', pk=book_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.book = book
            review.save()
            messages.success(request, 'Đã gửi đánh giá. Đánh giá sẽ được hiển thị sau khi được duyệt.')
            return redirect('library:book_detail', pk=book_id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/create_review.html', {'form': form, 'book': book})


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_pending_reviews_view(request):
    """Admin: pending reviews with search/sort."""
    qs = Review.objects.filter(status='PENDING').select_related('user', 'book')

    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(book__title__icontains=search) |
            Q(content__icontains=search)
        )

    sort = request.GET.get('sort', '-created_at')
    if sort in ['created_at', '-created_at', 'rating', '-rating']:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by('-created_at')

    return render(request, 'reviews/admin_pending_reviews.html', {
        'reviews': qs,
        'search': search,
        'sort': sort,
    })


@login_required
@user_passes_test(is_admin)
def approve_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, status='PENDING')

    if request.method == 'POST':
        review.status = 'APPROVED'
        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.save()
        messages.success(request, 'Đã duyệt đánh giá')
        return redirect('reviews:admin_pending')

    return render(request, 'reviews/approve_review.html', {'review': review})


@login_required
@user_passes_test(is_admin)
def reject_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, status='PENDING')

    if request.method == 'POST':
        review.status = 'REJECTED'
        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.save()
        messages.success(request, 'Đã từ chối đánh giá')
        return redirect('reviews:admin_pending')

    return render(request, 'reviews/reject_review.html', {'review': review})