from cart.models import Cart, Coupon
from rest_framework import serializers
from .vendor_serializer import VendorSerializer
from product.models import Product
from .product_serializer import ProductQuantitySerializer

class CouponSerializer(serializers.ModelSerializer):

    coupon_type = serializers.CharField(source="coupon_type.display_name")

    class Meta:
        model = Coupon
        fields = ["code", "description", "coupon_type", "discount_percentage", "discount_amount", "max_discount_amount", "min_order_amount", "valid_from", "valid_until"]

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