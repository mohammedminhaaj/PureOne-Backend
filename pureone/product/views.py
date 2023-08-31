from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from product.models import Product, ProductQuantity
from common.serializers import ProductOverviewSerializer, ProductSerializer
from rest_framework import status
from order.models import OrderFeedback
from django.db.models import Avg, OuterRef, Subquery, F, Q, Count
from django.contrib.contenttypes.models import ContentType
from vendor.models import Vendor
from order.helpers import get_average_rating
from common.utils import get_nearby_vendors
import json
from .helpers import filter_product

# Create your views here.


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_product(request: Request, product_name: str):
    try:
        # Subquery to get average rating for each product
        average_rating_subquery = OrderFeedback.objects.filter(
            content_type=ContentType.objects.get_for_model(Product),
            object_id=OuterRef("pk")
        ).values("object_id").annotate(
            avg_rating=Avg("rating")
        ).values("avg_rating")[:1]

        product = Product.all_objects.select_related("vendor", "vendor__vendor_status").prefetch_related(
            "product_quantity").annotate(average_rating=Subquery(average_rating_subquery)).get(name=product_name)
        serializer = ProductOverviewSerializer(product, many=False)
        if (product.vendor.vendor_status.name == "Closed"):
            return Response({"details": "The vendor is currently closed. Please come back after some time.", "product": serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        elif (product.vendor.vendor_status.name == "Busy"):
            return Response({"details": "The vendor is currently not accepting orders. Please come back after some time.", "product": serializer.data}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({"details": "Looks like the product does not exist."}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def filter_products(request: Request):
    current_latitude = request.query_params.get("lt")
    current_longitude = request.query_params.get("ln")
    page = request.query_params.get("page", 1)
    page = int(page) if isinstance(page, str) else page
    search_text = request.query_params.get("search_text", "")
    filter_query = request.query_params.get("filter_by")
    vendor_name = request.query_params.get("vendor")
    category_name = request.query_params.get("category")

    # Check if latitude and longitude information is present in query parameters
    if not current_latitude or not current_longitude or current_latitude == "null" or current_longitude == "null":
        return Response(data={"details": "Unable to fetch records."}, status=status.HTTP_400_BAD_REQUEST)

    vendors = Vendor.objects.filter(vendor_status__name="Open")
    regional_vendor_list = get_nearby_vendors(
        float(current_latitude), float(current_longitude), vendors)

    query = Q(productquantity__quantity__grams__lte=F(
        "available_quantity")) & Q(vendor__in=regional_vendor_list)
    if (len(search_text) >= 3):
        query = query & (Q(name__icontains=search_text) | Q(display_name__icontains=search_text) | Q(
            description__icontains=search_text) | Q(category__display_name__icontains=search_text) | Q(tags__icontains=search_text) | Q(vendor__display_name__icontains=search_text))

    # Subquery to get average rating for each product    
    average_product_rating_subquery = get_average_rating(ContentType.objects.get_for_model(Product))

    # Subquery to get the lowest product quantity
    product_quantity_subquery = ProductQuantity.objects.filter(product=OuterRef("pk")).select_related("quantity").only("quantity__display_name", "price", "original_price")[:1]

    products = Product.objects.filter(query).distinct().only("image", "display_name", "name", "category", "is_featured").annotate(
        average_rating=Subquery(average_product_rating_subquery),
        quantity=Subquery(product_quantity_subquery.values(
            "quantity__display_name")),
        price=Subquery(product_quantity_subquery.values("price")),
        original_price=Subquery(
            product_quantity_subquery.values("original_price")),
        order_count = Count("productquantity__cart__order"),
        discount = F("original_price") - F("price")
    )

    if filter_query and filter_query != "":
        products = filter_product(products, filter_query)

    if vendor_name and vendor_name != "":
        products = products.filter(vendor__display_name = vendor_name)

    if category_name and category_name != "":
        products = products.filter(category__display_name = category_name)
    
    serializer = ProductSerializer(products[(8*page)-8: 8*page], many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
