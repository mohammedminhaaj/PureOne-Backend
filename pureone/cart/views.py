from collections import defaultdict
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from product.models import ProductQuantity
from .models import Cart
from common.serializers import CartSerializer, CouponSerializer
from rest_framework import status
from common import constants
from common.utils import get_nearby_vendors
from .helpers import get_delivery_charge, validate_coupon, CouponError

# Create your views here.
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_cart(request: Request):
    # Initialize the response data
    response_data = {
        "cart": [],
        # Using defaultdict to simplify handling
        "vendor_errors": defaultdict(list),
        "delivery_charge": 0.0
    }

    # Get the cart data
    carts = Cart.objects.filter(user=request.user).select_related(
        "product_quantity", "product_quantity__product", "product_quantity__quantity", "product_quantity__product__vendor", "product_quantity__product__vendor__vendor_status")
    serializer = CartSerializer(carts, many=True)
    response_data["cart"] = serializer.data

    # Get the delivery charges
    response_data["delivery_charge"] = get_delivery_charge()

    vendors = {cart.product_quantity.product.vendor for cart in carts}
    vendor_status_map = {
        vendor.id: vendor.vendor_status.name for vendor in vendors}

    # Check if the location query parameters exist
    latitude = request.query_params.get("lt")
    longitude = request.query_params.get("ln")
    if latitude and longitude:
        nearby_vendors = set(get_nearby_vendors(float(latitude), float(longitude), vendors))
    else:
        nearby_vendors = set()

    # Check for any vendor errors
    for vendor in vendors:
        vendor_status = vendor_status_map[vendor.id]
        if vendor_status == "Closed":
            response_data["vendor_errors"]["CLOSED"].append(
                vendor.display_name)
        if vendor not in nearby_vendors:
            response_data["vendor_errors"]["UNDELIVERABLE"].append(
                vendor.display_name)

    # Convert vendor_errors from defaultdict to a regular dictionary for serialization
    response_data["vendor_errors"] = dict(response_data["vendor_errors"])

    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_edit_cart(request: Request, product_name: str | None = None):
    product_quantity_id = request.data.get("product_quantity_id")
    quantity_count = request.data.get("quantity_count")
    try:
        product_quantity = ProductQuantity.objects.select_related(
            "product", "quantity").get(pk=product_quantity_id)
        if (product_quantity.quantity.grams * quantity_count) > product_quantity.product.available_quantity:
            return Response(data={"details": "The vendor doesn't have enough quantity to serve you at the moment."}, status=status.HTTP_400_BAD_REQUEST)
        if product_name:
            cart = Cart.objects.get(
                user=request.user, product_quantity__product__name=product_name)
            cart.product_quantity = product_quantity
            cart.quantity_count = quantity_count
            cart.save(update_fields=["product_quantity", "quantity_count"])
        else:
            Cart.objects.create(user=request.user,
                                product_quantity=product_quantity, quantity_count=quantity_count)
        return Response(data={"details": f"Item {'added to' if not product_name else 'updated in'} cart"}, status=status.HTTP_201_CREATED)
    except (ProductQuantity.DoesNotExist, Cart.DoesNotExist):
        return Response(data={"details": "Selected quantity or cart item does not exists. Please refresh and try again."}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response(data={"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def edit_cart_quantity_count(request: Request, product_name: str):
    quantity_count = request.data.get("quantity_count")
    try:
        cart = Cart.objects.select_related("product_quantity", "product_quantity__product", "product_quantity__quantity").only(
            "product_quantity__quantity__grams", "product_quantity__product__available_quantity").get(user=request.user, product_quantity__product__name=product_name)
        if (cart.product_quantity.quantity.grams * quantity_count) > cart.product_quantity.product.available_quantity:
            return Response(data={"details": "The vendor doesn't have enough quantity to serve you at the moment."}, status=status.HTTP_400_BAD_REQUEST)
        cart.quantity_count = quantity_count
        cart.save(update_fields=["quantity_count"])
        return Response(data={"details": "Cart item updated successfully"}, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response(data={"details": "Cart item does not exists"}, status=status.HTTP_400_BAD_REQUEST)
    except Cart.MultipleObjectsReturned:
        return Response(data={"details": "Multiple cart items found with the same product"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response(data={"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_cart(request: Request):
    try:
        Cart.objects.get(user=request.user, product_quantity_id=request.data.get(
            "product_quantity_id")).delete()
    except Cart.DoesNotExist:
        pass
    except Exception:
        return Response(data={"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(data={"details": "Item removed successfully."}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_cart_using_vendor_list(request: Request):
    Cart.objects.filter(user=request.user, product_quantity__product__vendor__display_name__in=request.data.get(
        "vendor_list")).delete()
    return Response(data={"details": "Items removed successfully."}, status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def verify_coupon(request: Request):
    coupon_code = request.data.get("coupon")
    try:
        coupon = validate_coupon(user=request.user, coupon_code=coupon_code)
        serializer = CouponSerializer(coupon, many = False)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    except CouponError as e:
        return Response(data={"details": e.message}, status=e.status)
