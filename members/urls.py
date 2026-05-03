from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('join/', views.join_club_view, name='join_club'),
    path('my/', views.my_membership_view, name='my_membership'),
    path('admin/list/', views.admin_member_list_view, name='admin_members'),
    path('admin/pending/', views.admin_pending_view, name='admin_pending'),
    path('admin/approve/<int:pk>/', views.approve_member_view, name='approve'),
    path('admin/reject/<int:pk>/', views.reject_member_view, name='reject'),
    path('admin/points/<int:pk>/', views.adjust_points_view, name='adjust_points'),
]