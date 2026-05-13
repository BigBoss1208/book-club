import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from members.consumers import ClubChatConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')

application = ProtocolTypeRouter({
	"http": get_asgi_application(),
	"websocket": AuthMiddlewareStack(
		URLRouter([
			path('ws/club-chat/<int:club_id>/', ClubChatConsumer.as_asgi()),
		])
	),
})
