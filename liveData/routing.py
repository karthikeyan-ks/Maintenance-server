from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path
from liveData import Consumer  # Import your consumer

websocket_urlpatterns = [
    # Corrected WebSocket path pattern
    re_path(r'chat/$', Consumer.MyConsumer.as_asgi()),

    # Add more paths and corresponding consumers as needed
]
