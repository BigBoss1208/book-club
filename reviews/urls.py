from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:book_id>/', views.create_review_view, name='create_review'),
    path('admin/pending/', views.admin_pending_reviews_view, name='admin_pending'),
    path('admin/approve/<int:pk>/', views.approve_review_view, name='approve_review'),
    path('admin/reject/<int:pk>/', views.reject_review_view, name='reject_review'),
]