from django.urls import path
from . import views, consumers


urlpatterns = [
    path('place-order/cash/', views.place_order_cash, name='place_order_cash'),
    path('get-orders/', views.get_orders, name='get_orders'),
]
