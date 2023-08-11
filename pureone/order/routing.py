from django.urls import re_path
from .consumers import OrderConsumer

urlpatterns = [
    re_path(r"ws/order/get-updates/", OrderConsumer.as_asgi())
]
