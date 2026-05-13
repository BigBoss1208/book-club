from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('library/', include('library.urls')),
    path('borrowing/', include('borrowing.urls')),
    path('reviews/', include('reviews.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('members/', include(('members.urls', 'members'), namespace='members')),
    path('events/', include('events.urls')),
    path('leaderboard/', include(('leaderboard.urls', 'leaderboard'), namespace='leaderboard')),  # ← sửa
    path('chat/', include(('chat.urls', 'chat'), namespace='chat')),  # ← thêm
    path('reports/', include(('reports.urls', 'reports'), namespace='reports')),
    path('recommendations/', include(('recommendations.urls', 'recommendations'), namespace='recommendations')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)