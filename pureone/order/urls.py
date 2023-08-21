from django.urls import path
from . import views


urlpatterns = [
    path('place-order/cash/', views.place_order_cash, name='place_order_cash'),
    path('get-orders/', views.get_orders, name='get_orders'),
    path('get-previous-orders/', views.get_previous_orders, name='get_previous_orders'),
    path('add-order-feedback/', views.add_order_feedback, name='add_order_feedback'),
]
