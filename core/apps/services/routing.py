from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/pharmacy/<id>', consumers.ChannelConsumer.as_asgi()),
]