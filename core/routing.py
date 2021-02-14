from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.apps.services.token_auth import TokenAuthMiddleware
from django.urls import path

from core.apps.services.consumers import ChannelConsumer
from core.apps.services.routing import websocket_urlpatterns

application =  ProtocolTypeRouter({
    'websocket': TokenAuthMiddleware(
        URLRouter(
            websocket_urlpatterns
        ),
    ),
})
