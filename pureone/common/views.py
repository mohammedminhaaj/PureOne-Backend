from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from common.serializers import BannerSerializer, UserSerializer, ProductSerializer, CartSerializer
from .models import PromotionalBanner
from user.models import LoginAttempt
from django.utils.timezone import now, timedelta
from product.models import Product, Cart
from django.db.models import F

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_initial_state(request: Request):

    # for getting promotional banner data
    banners = PromotionalBanner.objects.only("banner").all()
    banner_serializer = BannerSerializer(banners, many=True)

    # for getting current logged in user data
    user_serializer = UserSerializer(request.user, many=False)

    # decides whether the update profile popup should be displayed or not.
    show_popup = (
        LoginAttempt.objects.filter(user=request.user).order_by(
            "-time").first().time > now() - timedelta(seconds=5)
        and (not request.user.email or request.user.username == request.user.mobile_number)
    )

    # for getting all products data in home page
    products = Product.objects.filter(productquantity__quantity__grams__lte=F(
        "available_quantity")).distinct().only("image", "display_name", "name")[:8]
    product_serializer = ProductSerializer(products, many=True)

    cart = Cart.objects.filter(user=request.user).select_related(
        "product_quantity", "product_quantity__product", "product_quantity__quantity")
    cart_serializer = CartSerializer(cart, many=True)

    return Response(data={
        "banner_images": banner_serializer.data,
        "user": user_serializer.data,
        "show_popup": show_popup,
        "all_products": product_serializer.data,
        "cart": cart_serializer.data,
    }, status=status.HTTP_200_OK)
