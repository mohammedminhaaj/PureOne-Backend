from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from product.models import Product, Cart, ProductQuantity
from common.serializers import ProductOverviewSerializer
from rest_framework import status
from common import constants
from django.db.models import F

# Create your views here.
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_product(request: Request, product_name: str):
    product = Product.all_objects.select_related("vendor").prefetch_related("product_quantity").get(name = product_name)
    serializer = ProductOverviewSerializer(product, many = False)
    return Response(data = serializer.data, status = status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_edit_cart(request: Request, product_name: str | None = None):
    product_quantity_id = request.data.get("product_quantity_id")
    try:
        product_quantity = ProductQuantity.objects.select_related("product", "quantity").get(pk = product_quantity_id)
        if product_quantity.quantity.grams > product_quantity.product.available_quantity:
            return Response(data = {"details": "We are currently out of stock. Sorry for the inconvenience."}, status=status.HTTP_400_BAD_REQUEST)
        if product_name:
            cart = Cart.objects.get(user = request.user, product_quantity__product__name = product_name)
            cart.product_quantity = product_quantity
            cart.save(update_fields = ["product_quantity"])
        else:
            Cart.objects.create(user = request.user, product_quantity = product_quantity)
        return Response(data = {"details": f"Item {'added to' if not product_name else 'updated in'} cart"}, status=status.HTTP_200_OK)
    except (ProductQuantity.DoesNotExist, Cart.DoesNotExist):
        return Response(data = {"details": "Selected quantity or cart item does not exists. Please refresh and try again."}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response(data = {"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_cart(request: Request):
    try:
        Cart.objects.get(user = request.user, product_quantity_id = request.data.get("product_quantity_id")).delete()
    except Cart.DoesNotExist:
        pass
    except Exception:
        return Response(data={"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(data={"details": "Item removed successfully."}, status = status.HTTP_200_OK)
