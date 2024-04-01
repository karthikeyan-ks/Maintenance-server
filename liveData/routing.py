from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from liveData import Consumer  # Import your consumer
from django.conf import settings
from django.conf.urls.static import static

websocket_urlpatterns = [
    # WebSocket path pattern with optional userid parameter
    re_path(r'^chat/(?P<userid>\w+)/$', Consumer.MyConsumer.as_asgi()),
]

# Optional: If you need to serve media files during development
urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
