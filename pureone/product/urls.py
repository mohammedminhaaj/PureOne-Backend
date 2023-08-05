from django.urls import path
from . import views

urlpatterns = [
    path("get-product/<str:product_name>/", views.get_product, name="get_product"),
    path("get-cart/", views.get_cart, name="get_cart"),
    path("add-cart/", views.add_edit_cart, name="add_cart"),
    path("edit-cart/<str:product_name>/", views.add_edit_cart, name="edit_cart"),
    path("edit-cart/quantity-count/<str:product_name>/", views.edit_cart_quantity_count, name="edit_cart_quantity_count"),
    path("delete-cart/", views.delete_cart, name="delete_cart"),
    path("delete-cart/vendor-list/", views.delete_cart_using_vendor_list, name="delete_cart_using_vendor_list"),
]