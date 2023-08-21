from cart.models import Cart
from rest_framework import serializers
from .vendor_serializer import VendorSerializer
from product.models import Product
from .product_serializer import ProductQuantitySerializer

class CartProduct(serializers.ModelSerializer):
    vendor = VendorSerializer(many = False, read_only = True)

    class Meta:
        model = Product
        fields = ["name", "display_name",
                  "image", "vendor"]


class CartSerializer(serializers.ModelSerializer):
    product = CartProduct(
        source='product_quantity.product', read_only=True)
    product_quantity = ProductQuantitySerializer()

    class Meta:
        model = Cart
        fields = ['product', 'product_quantity', "quantity_count", "order_price"]