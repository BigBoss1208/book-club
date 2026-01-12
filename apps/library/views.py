from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Book
from .forms import CategoryForm, BookForm

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def category_list(request):
    items = Category.objects.all().order_by("name")
    return render(request, "categories/category_list.html", {"items": items})

@user_passes_test(is_admin)
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tạo danh mục thành công.")
        return redirect("category_list")
    return render(request, "categories/category_form.html", {"form": form, "mode": "create"})

@user_passes_test(is_admin)
def category_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật danh mục thành công.")
        return redirect("category_list")
    return render(request, "categories/category_form.html", {"form": form, "mode": "edit"})

@user_passes_test(is_admin)
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Xóa danh mục thành công.")
        return redirect("category_list")
    return render(request, "categories/category_confirm_delete.html", {"obj": obj})


@user_passes_test(is_admin)
def book_list(request):
    items = Book.objects.select_related("category").all().order_by("-created_at")
    return render(request, "books/book_list.html", {"items": items})

@user_passes_test(is_admin)
def book_create(request):
    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        book = form.save(commit=False)
        book.created_by = request.user
        book.save()
        messages.success(request, "Tạo sách thành công.")
        return redirect("book_list")
    return render(request, "books/book_form.html", {"form": form, "mode": "create"})

@user_passes_test(is_admin)
def book_edit(request, pk):
    obj = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Cập nhật sách thành công.")
        return redirect("book_list")
    return render(request, "books/book_form.html", {"form": form, "mode": "edit"})

@user_passes_test(is_admin)
def book_delete(request, pk):
    obj = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Xóa sách thành công.")
        return redirect("book_list")
    return render(request, "books/book_confirm_delete.html", {"obj": obj})
