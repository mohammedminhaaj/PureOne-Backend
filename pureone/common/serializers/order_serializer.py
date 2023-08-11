from rest_framework import serializers
from order.models import Order
from .cart_serializer import CartSerializer
from cart.models import Cart

class OrderSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(source = "order_status.display_name")
    payment_mode = serializers.CharField(source = "payment_mode.display_name")

    def get_cart(self, obj):
        cart = Cart.all_objects.filter(order = obj, user = obj.user).select_related("product_quantity", "product_quantity__product", "product_quantity__quantity", "product_quantity__product__vendor", "product_quantity__product__vendor__vendor_status")
        serializer = CartSerializer(cart, many = True)
        return serializer.data

    def get_address(self, obj):
        if obj.building and obj.locality:
            return f"{obj.building}, {obj.locality}{f', {obj.landmark}' if obj.landmark else ''}"
        else:
            return obj.long_address

    address = serializers.SerializerMethodField()
    cart = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["order_id", "order_status", "payment_mode", "amount", "address", "cart", "created_at", "latitude", "longitude", "delivery_instructions"]