from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import Book, Category
from .forms import BookForm, CategoryForm
from borrowing.models import BorrowRequest


def is_admin(user):
    return user.is_staff


def _apply_book_filters(request, qs):
    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn__icontains=search)
        )
    category_id = request.GET.get('category')
    if category_id and category_id.isdigit():
        qs = qs.filter(category_id=category_id)
    elif category_id:
        category_id = ''
    sort = request.GET.get('sort', '-created_at')
    if sort == 'title':
        qs = qs.order_by('title')
    elif sort == 'popular':
        qs = qs.annotate(borrow_count=Count('borrow_requests')).order_by('-borrow_count')
    else:
        allowed_sorts = ['-created_at', 'created_at']
        if sort not in allowed_sorts:
            sort = '-created_at'
        qs = qs.order_by(sort)
    return qs, search, category_id, sort


def book_list_view(request):
    books = Book.objects.filter(is_active=True).select_related('category')
    books, search, category_id, sort = _apply_book_filters(request, books)
    paginator = Paginator(books, 12)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    categories = Category.objects.filter(is_active=True)
    context = {
        'books': books,
        'categories': categories,
        'search': search,
        'current_category': category_id,
        'current_sort': sort,
    }
    return render(request, 'library/book_list.html', context)


def book_export_csv_view(request):
    books = Book.objects.filter(is_active=True).select_related('category')
    books, search, category_id, sort = _apply_book_filters(request, books)
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="books_export.csv"'
    import csv
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['Title', 'Author', 'Category', 'Publisher', 'Publish Year', 'ISBN', 'Total Copies', 'Available Copies', 'Active'])
    for book in books:
        writer.writerow([
            book.title, book.author,
            book.category.name if book.category else '',
            book.publisher, book.publish_year,
            book.isbn or '', book.total_copies,
            book.available_copies,
            'Yes' if book.is_active else 'No',
        ])
    return response


def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk, is_active=True)
    if request.user.is_authenticated:
        reviews_qs = book.reviews.filter(
            Q(status='APPROVED') | Q(user=request.user)
        ).select_related('user')
    else:
        reviews_qs = book.reviews.filter(status='APPROVED').select_related('user')
    reviews_count = reviews_qs.count()
    reviews = reviews_qs.order_by('-created_at')[:10]
    context = {'book': book, 'reviews': reviews, 'reviews_count': reviews_count}
    return render(request, 'library/book_detail.html', context)


@login_required
def trending_view(request):
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    today_books = (
        BorrowRequest.objects.filter(request_date__date=today)
        .values('book', 'book__title', 'book__author')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:5]
    )
    week_books = (
        BorrowRequest.objects.filter(request_date__date__gte=week_start)
        .values('book', 'book__title', 'book__author')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:5]
    )
    month_books = (
        BorrowRequest.objects.filter(request_date__date__gte=month_start)
        .values('book', 'book__title', 'book__author')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:5]
    )
    all_time_books = (
        BorrowRequest.objects.values('book', 'book__title', 'book__author')
        .annotate(borrow_count=Count('id'))
        .order_by('-borrow_count')[:5]
    )
    return render(request, 'library/trending.html', {
        'today_books': today_books,
        'week_books': week_books,
        'month_books': month_books,
        'all_time_books': all_time_books,
    })


@login_required
@user_passes_test(is_admin)
def book_create_view(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            messages.success(request, f'Đã thêm sách "{book.title}"')
            return redirect('library:book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Thêm'})


@login_required
@user_passes_test(is_admin)
def book_update_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật sách "{book.title}"')
            return redirect('library:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'library/book_form.html', {'form': form, 'action': 'Cập nhật'})


@login_required
@user_passes_test(is_admin)
def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.is_active = False
        book.save()
        messages.success(request, f'Đã ẩn sách "{book.title}"')
        return redirect('library:book_list')
    return render(request, 'library/book_confirm_delete.html', {'book': book})


@login_required
@user_passes_test(is_admin)
def category_list_view(request):
    categories = Category.objects.annotate(book_count=Count('books'))
    search = request.GET.get('search', '')
    if search:
        categories = categories.filter(Q(name__icontains=search) | Q(description__icontains=search))
    active = request.GET.get('active', '')
    if active in ['1', '0']:
        categories = categories.filter(is_active=(active == '1'))
    sort = request.GET.get('sort', 'name')
    if sort == 'book_count':
        categories = categories.order_by('-book_count', 'name')
    elif sort == '-created_at':
        categories = categories.order_by('-created_at')
    else:
        categories = categories.order_by('name')
    return render(request, 'library/category_list.html', {
        'categories': categories, 'search': search, 'active': active, 'sort': sort,
    })


@login_required
@user_passes_test(is_admin)
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Đã thêm danh mục "{category.name}"')
            return redirect('library:category_list')
    else:
        form = CategoryForm()
    return render(request, 'library/category_form.html', {'form': form, 'action': 'Thêm'})


@login_required
@user_passes_test(is_admin)
def category_update_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã cập nhật danh mục "{category.name}"')
            return redirect('library:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'library/category_form.html', {'form': form, 'action': 'Cập nhật'})


@login_required
@user_passes_test(is_admin)
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    has_active_books = category.books.filter(is_active=True).exists()
    if has_active_books:
        messages.error(request, 'Không thể ẩn danh mục vì vẫn còn sách đang hoạt động trong danh mục này.')
        return redirect('library:category_list')
    if request.method == 'POST':
        category.is_active = False
        category.save()
        messages.success(request, f'Đã ẩn danh mục "{category.name}"')
        return redirect('library:category_list')
    return render(request, 'library/category_confirm_delete.html', {'category': category})