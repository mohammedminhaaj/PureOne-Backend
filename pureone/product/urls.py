from django.urls import path
from . import views

urlpatterns = [
    path("get-product/<str:product_name>/", views.get_product, name="get_product"),
    path("add-cart/", views.add_edit_cart, name="add_cart"),
    path("edit-cart/<str:product_name>/", views.add_edit_cart, name="edit_cart"),
    path("delete-cart/", views.delete_cart, name="delete_cart"),
]