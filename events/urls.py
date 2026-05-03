from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.public_event_list_view, name='public_list'),
    path('admin/', views.event_list_view, name='event_list'),
    path('admin/create/', views.event_create_view, name='event_create'),
    path('admin/<int:pk>/', views.event_detail_view, name='event_detail'),
    path('admin/<int:pk>/qr.png', views.event_qr_view, name='event_qr'),
    path('checkin/<uuid:token>/', views.checkin_view, name='checkin'),
]