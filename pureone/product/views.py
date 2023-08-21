from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from product.models import Product
from common.serializers import ProductOverviewSerializer
from rest_framework import status
from order.models import OrderFeedback
from django.db.models import Avg, OuterRef, Subquery
from django.contrib.contenttypes.models import ContentType

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

