from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from django.db.models import Q
from .models import BorrowRequest, BorrowTransaction
from .forms import BorrowRequestForm, RejectRequestForm  # ✅ Thêm RejectRequestForm
from library.models import Book


@login_required
def create_borrow_request_view(request, book_id):
    book = get_object_or_404(Book, pk=book_id, is_active=True)

    if not book.is_available:
        messages.error(request, 'Sách này hiện không còn sẵn')
        return redirect('library:book_detail', pk=book_id)

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


@login_required
def user_return_book_view(request, pk):
    transaction = get_object_or_404(BorrowTransaction, pk=pk)

    if transaction.status not in ['BORROWING', 'OVERDUE', 'RETURN_PENDING']:
        messages.error(request, 'Giao dịch này không thể trả sách!')
        return redirect('borrowing:my_requests')

    if request.method == 'POST':
        transaction.returned_at = timezone.now()
        transaction.status = 'RETURNED'
        transaction.save()
        transaction.calculate_fine()

        transaction.borrow_request.status = 'RETURNED'
        transaction.borrow_request.save()

        book = transaction.borrow_request.book
        book.available_copies += 1
        book.save()
        messages.success(request, 'Đã gửi yêu cầu trả sách thành công!')
        return redirect('borrowing:my_requests')

    return render(request, 'borrowing/user_return_book.html', {'transaction': transaction})


# Admin views
def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_pending_requests_view(request):
    qs = BorrowRequest.objects.filter(status='PENDING').select_related('user', 'book')

    search = request.GET.get('search', '').strip()
    if search:
        qs = qs.filter(
            Q(user__username__icontains=search) |
            Q(book__title__icontains=search)
        )

    sort = request.GET.get('sort', '-request_date')
    allowed_sorts = ['-request_date', 'request_date', 'expected_return_date', '-expected_return_date']
    if sort not in allowed_sorts:
        sort = '-request_date'
    qs = qs.order_by(sort)

    return render(request, 'borrowing/admin_pending_requests.html', {
        'requests': qs,
        'search': search,
        'sort': sort,
    })


@login_required
@user_passes_test(is_admin)
def approve_borrow_request_view(request, pk):
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, status='PENDING')
    book = borrow_request.book

    if not book.is_available:
        messages.error(request, 'Sách không còn sẵn')
        return redirect('borrowing:admin_pending')

    if request.method == 'POST':
        borrow_request.status = 'APPROVED'
        borrow_request.handled_by = request.user
        borrow_request.handled_at = timezone.now()
        borrow_request.save()

        due_date = timezone.now() + timedelta(days=(borrow_request.expected_return_date - timezone.now().date()).days)
        BorrowTransaction.objects.create(
            borrow_request=borrow_request,
            due_at=due_date,
            status='BORROWING'
        )

        book.available_copies -= 1
        book.save()

        if borrow_request.user.email:
            subject = 'Yêu cầu mượn sách đã được duyệt'
            message = (
                f'Xin chào {borrow_request.user.username},\n\n'
                f'Yêu cầu mượn sách "{book.title}" của bạn đã được duyệt.\n'
                f'Ngày trả dự kiến: {borrow_request.expected_return_date:%d/%m/%Y}.\n\n'
                'Cảm ơn bạn.'
            )
            send_mail(
                subject,
                message,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@bookclub.local'),
                [borrow_request.user.email],
                fail_silently=True,
            )

        messages.success(request, f'Đã duyệt yêu cầu mượn sách cho {borrow_request.user.username}')
        return redirect('borrowing:admin_pending')

    return render(request, 'borrowing/approve_request.html', {'request': borrow_request})


@login_required
@user_passes_test(is_admin)
def reject_borrow_request_view(request, pk):
    borrow_request = get_object_or_404(BorrowRequest, pk=pk, status='PENDING')

    if request.method == 'POST':
        form = RejectRequestForm(request.POST)
        if form.is_valid():
            borrow_request.status = 'REJECTED'
            borrow_request.handled_by = request.user
            borrow_request.handled_at = timezone.now()
            borrow_request.reject_reason = form.cleaned_data['reject_reason']  # ✅
            borrow_request.save()

            if borrow_request.user.email:
                subject = 'Yêu cầu mượn sách bị từ chối'
                message = (
                    f'Xin chào {borrow_request.user.username},\n\n'
                    f'Yêu cầu mượn sách "{borrow_request.book.title}" của bạn đã bị từ chối.\n'
                    f'Lý do: {borrow_request.reject_reason}\n\n'  # ✅
                    'Vui lòng liên hệ quản trị nếu cần hỗ trợ thêm.\n\n'
                    'Cảm ơn bạn.'
                )
                send_mail(
                    subject,
                    message,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@bookclub.local'),
                    [borrow_request.user.email],
                    fail_silently=True,
                )

            messages.success(request, 'Đã từ chối yêu cầu')
            return redirect('borrowing:admin_pending')
    else:
        form = RejectRequestForm()

    return render(request, 'borrowing/reject_request.html', {
        'request': borrow_request,
        'form': form,
    })


@login_required
@user_passes_test(is_admin)
def admin_active_transactions_view(request):
    qs = BorrowTransaction.objects.filter(
        status__in=['BORROWING', 'OVERDUE']
    ).select_related('borrow_request__user', 'borrow_request__book')

    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(borrow_request__user__username__icontains=search) |
            Q(borrow_request__user__email__icontains=search) |
            Q(borrow_request__book__title__icontains=search)
        )

    status = request.GET.get('status', '')
    if status in ['BORROWING', 'OVERDUE']:
        qs = qs.filter(status=status)

    sort = request.GET.get('sort', 'due_at')
    if sort in ['due_at', '-due_at', 'borrowed_at', '-borrowed_at']:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by('due_at')

    return render(request, 'borrowing/admin_transactions.html', {
        'transactions': qs,
        'search': search,
        'status': status,
        'sort': sort,
    })


@login_required
@user_passes_test(is_admin)
def return_book_view(request, pk):
    transaction = get_object_or_404(BorrowTransaction, pk=pk, status__in=['BORROWING', 'OVERDUE'])

    if request.method == 'POST':
        transaction.returned_at = timezone.now()
        transaction.status = 'RETURNED'
        transaction.save()
        transaction.calculate_fine()

        book = transaction.borrow_request.book
        book.available_copies += 1
        book.save()

        messages.success(request, 'Đã xác nhận trả sách')
        return redirect('borrowing:admin_transactions')

    return render(request, 'borrowing/return_book.html', {'transaction': transaction})