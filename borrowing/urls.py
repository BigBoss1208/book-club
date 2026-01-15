from django.urls import path
from . import views

app_name = 'borrowing'

urlpatterns = [
    path('request/<int:book_id>/', views.create_borrow_request_view, name='create_request'),
    path('my-requests/', views.my_borrow_requests_view, name='my_requests'),
    path('cancel/<int:pk>/', views.cancel_borrow_request_view, name='cancel_request'),

    # Admin
    path('admin/pending/', views.admin_pending_requests_view, name='admin_pending'),
    path('admin/approve/<int:pk>/', views.approve_borrow_request_view, name='approve_request'),
    path('admin/reject/<int:pk>/', views.reject_borrow_request_view, name='reject_request'),
    path('admin/transactions/', views.admin_active_transactions_view, name='admin_transactions'),
    path('admin/return/<int:pk>/', views.return_book_view, name='return_book'),
]