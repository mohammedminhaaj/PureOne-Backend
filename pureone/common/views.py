from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from common.serializers import BannerSerializer, ProductSerializer, CartSerializer, CategorySerializer, NearbyVendorSerializer
from common.utils import get_nearby_vendors
from .models import PromotionalBanner
from vendor.models import Vendor
from product.models import Product, ProductQuantity
from cart.models import Cart
from django.db.models import F, Count, Q
from fcm_django.models import FCMDevice, DeviceType
from common import constants
from django.db.models import OuterRef, Subquery
from order.helpers import get_average_rating
from django.contrib.contenttypes.models import ContentType

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_home_screen(request: Request):

    # Initializing the response data
    response_data = {
        "banner_images": [],
        "show_popup": False,
        "featured_products": [],
        "all_products": [],
        "categories": [],
        "nearby_vendors": [],
        "top_selling": [],
        "top_rated": [],
        "cart": [],
    }

    current_latitude = request.query_params.get("lt")
    current_longitude = request.query_params.get("ln")

    # Check if latitude and longitude information is present in query parameters
    if not current_latitude or not current_longitude or current_latitude == "null" or current_longitude == "null":
        return response_data
    
    content_types_dict = {content_type.model: content_type for content_type in ContentType.objects.filter(Q(app_label="vendor", model="Vendor") | Q(app_label="product", model="Product"))}

    # for getting promotional banner data
    banners = PromotionalBanner.objects.only("banner").all()
    banner_serializer = BannerSerializer(banners, many=True)
    response_data["banner_images"] = banner_serializer.data

    # Subquery to get average vendor rating for each product
    average_vendor_rating_subquery = get_average_rating(content_types_dict["vendor"])

    vendors = Vendor.objects.filter(vendor_status__name="Open").only(
        "id", "name", "display_name", "latitude", "longitude").annotate(average_rating = Subquery(average_vendor_rating_subquery))
    regional_vendor_list = get_nearby_vendors(
        float(current_latitude), float(current_longitude), vendors)
    
    # For getting nearby vendor data
    vendor_serializer = NearbyVendorSerializer(regional_vendor_list[:8], many = True, current_latitude = float(current_latitude), current_longitude = float(current_longitude))
    response_data["nearby_vendors"] = vendor_serializer.data

    # Subquery to get average product rating for each product
    average_product_rating_subquery = get_average_rating(content_types_dict["product"])

    # Subquery to get the lowest product quantity
    product_quantity_subquery = ProductQuantity.objects.filter(product=OuterRef("pk")).select_related("quantity").only("quantity__display_name", "price", "original_price")[:1]

    # for getting all products data which will be later used for filtering
    all_products = Product.objects.select_related("category").filter(productquantity__quantity__grams__lte=F(
        "available_quantity"), vendor__in=regional_vendor_list).distinct().only("image", "display_name", "name", "category", "is_featured").annotate(
        average_rating=Subquery(average_product_rating_subquery),
        quantity = Subquery(product_quantity_subquery.values("quantity__display_name")),
        price = Subquery(product_quantity_subquery.values("price")),
        original_price = Subquery(product_quantity_subquery.values("original_price")),
    )

    # Get only 8 categories to display in categories section
    categories = []
    for product in all_products:
        if len(categories) >= 8:
            break
        category = product.category
        if category not in categories:
            categories.append(category)
    category_serializer = CategorySerializer(categories, many = True)
    response_data["categories"] = category_serializer.data

    # Get only the first 8 featured products to display in featured products
    featured_products = [product for product in all_products if product.is_featured][:8]
    featured_product_serializer = ProductSerializer(featured_products, many = True)
    response_data["featured_products"] = featured_product_serializer.data

    # Get only the first 8 products to display in top selling products
    top_selling_products = all_products.annotate(order_count = Count("productquantity__cart__order")).order_by("-order_count")[:8]
    top_selling_serializer = ProductSerializer(top_selling_products, many = True)
    response_data["top_selling"] = top_selling_serializer.data

    # Get only the first 8 products to display in top rated products
    top_rated_products = all_products.filter(average_rating__gt = 0).order_by("-average_rating")[:8]
    top_rated_serializer = ProductSerializer(top_rated_products, many = True)
    response_data["top_rated"] = top_rated_serializer.data

    # Get only the first 8 products to display in all products
    products = all_products[:8]
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
