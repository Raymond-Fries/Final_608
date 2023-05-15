from django.urls import path
from .consumers import real_time_consumer

ws_urlpatterns = [
    path('ws/real_time/',real_time_consumer.as_asgi()),

]
