from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from common.serializers import BannerSerializer, ProductSerializer, CartSerializer
from common.utils import haversine
from .models import PromotionalBanner
from vendor.models import Vendor
from product.models import Product, ProductQuantity
from cart.models import Cart
from django.db.models import F
from fcm_django.models import FCMDevice, DeviceType
from common import constants
from django.db.models import Avg, OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType
from order.models import OrderFeedback

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_home_screen(request: Request):

    # Initializing the response data
    response_data = {
        "banner_images": [],
        "show_popup": False,
        "all_products": [],
        "cart": [],
    }

    current_latitude = request.query_params.get("lt")
    current_longitude = request.query_params.get("ln")

    # Check if latitude and longitude information is present in query parameters
    if not current_latitude or not current_longitude or current_latitude == "null" or current_longitude == "null":
        return response_data

    # for getting promotional banner data
    banners = PromotionalBanner.objects.only("banner").all()
    banner_serializer = BannerSerializer(banners, many=True)
    response_data["banner_images"] = banner_serializer.data

    vendors = Vendor.objects.filter(vendor_status__name="Open").only(
        "id", "name", "latitude", "longitude")
    vendor_names: list = []
    co_ordinates: list = []

    for vendor in vendors:
        vendor_names.append(vendor.name)
        co_ordinates.append((vendor.latitude, vendor.longitude,))

    regional_vendor_list = haversine(
        float(current_latitude), float(current_longitude), co_ordinates)

    regional_vendors = filter(lambda q: (
        q.latitude, q.longitude,) in regional_vendor_list, vendors)

    # Subquery to get average rating for each product
    average_rating_subquery = OrderFeedback.objects.filter(
        content_type=ContentType.objects.get_for_model(Product),
        object_id=OuterRef("pk")
    ).values("object_id").annotate(
        avg_rating=Avg("rating")
    ).values("avg_rating")[:1]

    # Subquery to get the lowest product quantity
    product_quantity_subquery = ProductQuantity.objects.filter(product=OuterRef("pk")).select_related("quantity").only("quantity__display_name", "price", "original_price")[:1]

    # for getting all products data in home page
    products = Product.objects.filter(productquantity__quantity__grams__lte=F(
        "available_quantity"), vendor__in=regional_vendors).distinct().only("image", "display_name", "name").annotate(
        average_rating=Subquery(average_rating_subquery),
        quantity = Subquery(product_quantity_subquery.values("quantity__display_name")),
        price = Subquery(product_quantity_subquery.values("price")),
        original_price = Subquery(product_quantity_subquery.values("original_price")),
    )[:8]

    product_serializer = ProductSerializer(products, many=True)
    response_data["all_products"] = product_serializer.data

    # for getting all cart data corresponding to the user
    cart = Cart.objects.filter(user=request.user).select_related(
        "product_quantity", "product_quantity__product", "product_quantity__quantity", "product_quantity__product__vendor", "product_quantity__product__vendor__vendor_status")
    cart_serializer = CartSerializer(cart, many=True)
    response_data["cart"] = cart_serializer.data

    return Response(data=response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_fcm_token(request: Request):
    platform_dict = {
        "android": DeviceType.ANDROID,
        "ios": DeviceType.IOS,
        "web": DeviceType.WEB
    }
    try:
        FCMDevice.objects.get_or_create(user=request.user, type=platform_dict.get(
            request.data.get("platform")), registration_id=request.data.get("registration_id"))
        return Response(data={"details": "Device registered successfully"}, status=status.HTTP_200_OK)
    except Exception:
        return Response(data={"details": constants.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
