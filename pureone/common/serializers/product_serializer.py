from product.models import Product, ProductQuantity, Category, Quantity
from rest_framework import serializers
from typing import Any
from .vendor_serializer import VendorSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["display_name", "image"]


class ProductQuantitySerializer(serializers.ModelSerializer):

    quantity = serializers.CharField(source="quantity.display_name")

    class Meta:
        model = ProductQuantity
        fields = ["id", "quantity", "price", "original_price"]


class QuantitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Quantity
        fields = ["display_name"]


class ProductSerializer(serializers.ModelSerializer):

    product_quantity = serializers.SerializerMethodField()

    def get_product_quantity(self, obj):
        product_quantities = ProductQuantity.objects.select_related("quantity").filter(product=obj).order_by(
            "quantity__grams").only("quantity_id", "quantity__grams", "quantity__display_name", "price", "original_price").first()
        serializer = ProductQuantitySerializer(product_quantities, many=False)
        return serializer.data

    class Meta:
        model = Product
        fields = ["image", "display_name", "name", "product_quantity"]


class ProductOverviewSerializer(serializers.ModelSerializer):

    vendor = VendorSerializer(many = False, read_only = True)
    product_quantity = serializers.SerializerMethodField()

    def get_product_quantity(self, obj):
        product_quantities = ProductQuantity.objects.select_related("quantity").filter(product=obj, quantity__grams__lte=obj.available_quantity).order_by(
        "quantity__grams").only("quantity_id", "quantity__grams", "quantity__display_name", "price", "original_price")
        serializer = ProductQuantitySerializer(
            product_quantities, many=True)
        return serializer.data

    class Meta:
        model = Product
        fields = ["image", "name", "display_name", "description",
                  "vendor", "product_quantity", "deleted_at"]


