from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from liveData import Consumer  # Import your consumer
from django.conf import settings
from django.conf.urls.static import static
websocket_urlpatterns = [
    # Corrected WebSocket path pattern
    re_path(r'chat/$', Consumer.MyConsumer.as_asgi()),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
