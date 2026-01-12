from django.urls import path
from .views import (
    category_list, category_create, category_edit, category_delete,
    book_list, book_create, book_edit, book_delete
)

urlpatterns = [
    path("categories/", category_list, name="category_list"),
    path("categories/create/", category_create, name="category_create"),
    path("categories/<int:pk>/edit/", category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", category_delete, name="category_delete"),

    path("manage/", book_list, name="book_list"),
    path("manage/create/", book_create, name="book_create"),
    path("manage/<int:pk>/edit/", book_edit, name="book_edit"),
    path("manage/<int:pk>/delete/", book_delete, name="book_delete"),
]
