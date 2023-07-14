from django.urls import path
from . import views

urlpatterns = [
    path("get-product/<str:product_name>/", views.get_product, name="get_product"),
]