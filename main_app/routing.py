from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/chat/(?P<room_id>\d+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"^ws/alerts/$", consumers.AlertsConsumer.as_asgi()),
    re_path(r"^ws/pc-notifications/$", consumers.PCNotificationConsumer.as_asgi()),
    re_path(r"^ws/booking-status/$", consumers.BookingStatusConsumer.as_asgi()),
    re_path(r"^ws/pc-status-updates/$", consumers.PCStatusBroadcastConsumer.as_asgi()),
]
