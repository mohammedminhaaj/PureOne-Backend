from product.models import Product, ProductQuantity, Category, Quantity, Cart
from rest_framework import serializers
from typing import Any


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


def get_product_quantities(obj: Any):
    return ProductQuantity.objects.select_related("quantity").filter(product=obj, quantity__grams__lte=obj.available_quantity).order_by(
        "quantity__grams").only("quantity_id", "quantity__grams", "quantity__display_name", "price", "original_price")


class ProductOverviewSerializer(serializers.ModelSerializer):

    vendor = serializers.CharField(source="vendor.display_name")
    product_quantity = serializers.SerializerMethodField()

    def get_product_quantity(self, obj):
        product_quantities = get_product_quantities(obj)
        serializer = ProductQuantitySerializer(
            product_quantities, many=True)
        return serializer.data

    class Meta:
        model = Product
        fields = ["image", "name", "display_name", "description",
                  "vendor", "product_quantity", "deleted_at"]


class CartProduct(serializers.ModelSerializer):
    vendor = serializers.CharField(source="vendor.display_name")
    product_quantity = serializers.SerializerMethodField()

    def get_product_quantity(self, obj):
        product_quantities = get_product_quantities(obj)
        serializer = ProductQuantitySerializer(
            product_quantities, many=True)
        return serializer.data

    class Meta:
        model = Product
        fields = ["name", "display_name",
                  "image", "vendor", "product_quantity"]


class CartSerializer(serializers.ModelSerializer):
    product = CartProduct(
        source='product_quantity.product', read_only=True)
    product_quantity = ProductQuantitySerializer()

    class Meta:
        model = Cart
        fields = ['product', 'product_quantity']
