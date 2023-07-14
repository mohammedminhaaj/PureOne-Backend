from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from product.models import Product
from common.serializers import ProductOverviewSerializer
from rest_framework import status

# Create your views here.
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_product(request: Request, product_name: str):
    product = Product.objects.select_related("vendor").prefetch_related("product_quantity").get(name = product_name)
    serializer = ProductOverviewSerializer(product, many = False)
    return Response(data = serializer.data, status = status.HTTP_200_OK)