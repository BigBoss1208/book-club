from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Book, Category
from .forms import BookForm, CategoryForm


def is_admin(user):
    return user.is_staff


def book_list_view(request):
    books = Book.objects.filter(is_active=True).select_related('category')

    # Search
    search = request.GET.get('search', '')
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(author__icontains=search) |
            Q(isbn__icontains=search)
        )

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        books = books.filter(category_id=category_id)

    # Sort
    sort = request.GET.get('sort', '-created_at')
    if sort == 'title':
        books = books.order_by('title')
    elif sort == 'popular':
        books = books.annotate(borrow_count=Count('borrow_requests')).order_by('-borrow_count')
    else:
        books = books.order_by(sort)

    # Pagination
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


def book_detail_view(request, pk):
    book = get_object_or_404(Book, pk=pk, is_active=True)
    reviews = book.reviews.filter(status='APPROVED').select_related('user')[:10]

    context = {
        'book': book,
        'reviews': reviews,
    }
    return render(request, 'library/book_detail.html', context)


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


# Category Views
@login_required
@user_passes_test(is_admin)
def category_list_view(request):
    categories = Category.objects.annotate(book_count=Count('books'))
    return render(request, 'library/category_list.html', {'categories': categories})


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