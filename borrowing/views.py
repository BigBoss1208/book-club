from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import BorrowRequest, BorrowTransaction
from .forms import BorrowRequestForm
from library.models import Book


@login_required
def create_borrow_request_view(request, book_id):
    book = get_object_or_404(Book, pk=book_id, is_active=True)

    # Check if book is available
    if not book.is_available:
        messages.error(request, 'Sách này hiện không còn sẵn')
        return redirect('library:book_detail', pk=book_id)

    # Check if user already has pending/approved request for this book
    existing = BorrowRequest.objects.filter(
        user=request.user,
        book=book,
        status__in=['PENDING', 'APPROVED']
    ).exists()
    if existing:
        messages.warning(request, 'Bạn đã có yêu cầu mượn sách này rồi')
        return redirect('library:book_detail', pk=book_id)

    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            borrow_request = form.save(commit=False)
            borrow_request.user = request.user
            borrow_request.book = book
            borrow_request.save()
            messages.success(request, 'Đã gửi yêu cầu mượn sách')
            return redirect('borrowing:my_requests')
    else:
        form = BorrowRequestForm()

    return render(request, 'borrowing/create_request.html', {'form': form, 'book': book})


@login_required
def my_borrow_requests_view(request):
    requests = BorrowRequest.objects.filter(user=request.user).select_related('book', 'handled_by')
    return render(request, 'borrowing/my_requests.html', {'requests': requests})


@login_required
def cancel_borrow_request_view(request, pk):
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, user=request.user)
    if borrow_request.status != 'PENDING':
        messages.error(request, 'Chỉ có thể huỷ yêu cầu đang chờ')
        return redirect('borrowing:my_requests')

    if request.method == 'POST':
        borrow_request.status = 'CANCELLED'
        borrow_request.save()
        messages.success(request, 'Đã huỷ yêu cầu')
        return redirect('borrowing:my_requests')

    return render(request, 'borrowing/cancel_request.html', {'request': borrow_request})


# Admin views
def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_pending_requests_view(request):
    requests = BorrowRequest.objects.filter(status='PENDING').select_related('user', 'book')
    return render(request, 'borrowing/admin_pending_requests.html', {'requests': requests})


@login_required
@user_passes_test(is_admin)
def approve_borrow_request_view(request, pk):
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, status='PENDING')
    book = borrow_request.book

    if not book.is_available:
        messages.error(request, 'Sách không còn sẵn')
        return redirect('borrowing:admin_pending')

    if request.method == 'POST':
        # Update request
        borrow_request.status = 'APPROVED'
        borrow_request.handled_by = request.user
        borrow_request.handled_at = timezone.now()
        borrow_request.save()

        # Create transaction
        due_date = timezone.now() + timedelta(days=(borrow_request.expected_return_date - timezone.now().date()).days)
        BorrowTransaction.objects.create(
            borrow_request=borrow_request,
            due_at=due_date
        )

        # Update book availability
        book.available_copies -= 1
        book.save()

        messages.success(request, f'Đã duyệt yêu cầu mượn sách cho {borrow_request.user.username}')
        return redirect('borrowing:admin_pending')

    return render(request, 'borrowing/approve_request.html', {'request': borrow_request})


@login_required
@user_passes_test(is_admin)
def reject_borrow_request_view(request, pk):
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, status='PENDING')

    if request.method == 'POST':
        borrow_request.status = 'REJECTED'
        borrow_request.handled_by = request.user
        borrow_request.handled_at = timezone.now()
        borrow_request.save()
        messages.success(request, 'Đã từ chối yêu cầu')
        return redirect('borrowing:admin_pending')

    return render(request, 'borrowing/reject_request.html', {'request': borrow_request})


@login_required
@user_passes_test(is_admin)
def admin_active_transactions_view(request):
    transactions = BorrowTransaction.objects.filter(
        status__in=['BORROWING', 'OVERDUE']
    ).select_related('borrow_request__user', 'borrow_request__book')
    return render(request, 'borrowing/admin_transactions.html', {'transactions': transactions})


@login_required
@user_passes_test(is_admin)
def return_book_view(request, pk):
    transaction = get_object_or_404(BorrowTransaction, pk=pk, status__in=['BORROWING', 'OVERDUE'])

    if request.method == 'POST':
        transaction.returned_at = timezone.now()
        transaction.status = 'RETURNED'
        transaction.calculate_fine()
        transaction.save()

        # Update book availability
        book = transaction.borrow_request.book
        book.available_copies += 1
        book.save()

        messages.success(request, 'Đã xác nhận trả sách')
        return redirect('borrowing:admin_transactions')

    return render(request, 'borrowing/return_book.html', {'transaction': transaction})