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
from product.models import Product, Cart
from django.db.models import F

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_home_screen(request: Request):

    #Initializing the response data
    response_data = {
        "banner_images": [],
        "show_popup": False,
        "all_products": [],
        "cart": [],
    }

    current_latitude = request.query_params.get("lt")
    current_longitude = request.query_params.get("ln")

    #Check if latitude and longitude information is present in query parameters
    if not current_latitude or not current_longitude or current_latitude == "null" or current_longitude == "null":
        return response_data

    # for getting promotional banner data
    banners = PromotionalBanner.objects.only("banner").all()
    banner_serializer = BannerSerializer(banners, many=True)
    response_data["banner_images"] = banner_serializer.data

    vendors = Vendor.objects.filter(vendor_status__name = "Open").only("id", "name", "latitude", "longitude")
    vendor_names: list = []
    co_ordinates: list = []

    for vendor in vendors:
        vendor_names.append(vendor.name)
        co_ordinates.append((vendor.latitude, vendor.longitude,))

    regional_vendor_list = haversine(float(current_latitude), float(current_longitude), co_ordinates)

    regional_vendors = filter(lambda q: (q.latitude, q.longitude,) in regional_vendor_list ,vendors)

    # for getting all products data in home page
    products = Product.objects.filter(productquantity__quantity__grams__lte=F(
        "available_quantity"), vendor__in = regional_vendors).distinct().only("image", "display_name", "name")[:8]
    product_serializer = ProductSerializer(products, many=True)
    response_data["all_products"] = product_serializer.data

    #for getting all cart data corresponding to the user
    cart = Cart.objects.filter(user=request.user).select_related(
        "product_quantity", "product_quantity__product", "product_quantity__quantity")
    cart_serializer = CartSerializer(cart, many = True)
    response_data["cart"] = cart_serializer.data

    return Response(data=response_data, status=status.HTTP_200_OK)
