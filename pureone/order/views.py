from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart
from rest_framework import status
from common.models import MasterData
from .models import Order, OrderFeedback
from common.serializers.order_serializer import OrderSerializer
from cart.helpers import get_delivery_charge
from decimal import Decimal
from product.models import Product
from vendor.models import Vendor
from django.db.models import Case, When, Value, BooleanField

# Create your views here.


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def place_order_cash(request: Request):

    # Get the cart data
    carts = Cart.objects.filter(user=request.user).select_related(
        "product_quantity", "product_quantity__product", "product_quantity__quantity", "product_quantity__product__vendor", "product_quantity__product__vendor__vendor_status")

    amount = 0

    # Validate the order and calculate the amount
    for cart in carts:
        if cart.product_quantity.quantity.grams > cart.product_quantity.product.available_quantity:
            return Response(data={"details": "One or more items are out of stock. Please refresh."}, status=status.HTTP_400_BAD_REQUEST)
        elif cart.product_quantity.product.vendor.vendor_status.name != "Open":
            return Response(data={"details": "One or more vendors are unserviceable. Please refresh."}, status=status.HTTP_400_BAD_REQUEST)

        amount += cart.product_quantity.price * cart.quantity_count

    # Fire a single query to fetch both records from master data
    base_qs = MasterData.objects.select_related("master_category").filter(
        name__in=["Placed", "Cash"], master_category__name__in=["Order Status", "Payment Mode"])

    # Generate a dictionary to separate both master data
    base_qs_dict = {qs.name: qs for qs in base_qs}

    order_status = base_qs_dict.get("Placed")
    payment_mode = base_qs_dict.get("Cash")

    try:
        # Create the order object
        order = Order.objects.create(
            user=request.user,
            order_status=order_status,
            payment_mode=payment_mode,
            amount=amount,
            delivery_charge=Decimal(get_delivery_charge()),
            latitude=request.data.get("latitude"),
            longitude=request.data.get("longitude"),
            short_address=request.data.get("short_address"),
            long_address=request.data.get("long_address"),
            building=request.data.get("building"),
            locality=request.data.get("locality"),
            landmark=request.data.get("landmark"),
            delivery_instructions=request.data.get("delivery_instructions")
        )

        # update cart objects with the newly created order object and order price
        for cart in carts:
            cart.order = order
            cart.order_price = cart.product_quantity.price

        Cart.objects.bulk_update(carts, ["order", "order_price"])

        return Response(data={"details": "Order placed"}, status=status.HTTP_201_CREATED)
    except Exception:
        return Response(data={"details": "Error occured while placing order"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_orders(request: Request):
    base_qs = Order.objects.prefetch_related("orderfeedback_set").select_related("order_status", "payment_mode", "user").filter(user=request.user).annotate(
        has_feedback=Case(When(orderfeedback__isnull=False, then=Value(True)), default=Value(False), output_field=BooleanField(),)).distinct()
    pending = base_qs.exclude(order_status__name__in=[
                              "Delivered", "Undelivered", "Rejected"])
    previous = base_qs.filter(order_status__name__in=[
                              "Delivered", "Undelivered", "Rejected"])[:6]
    pending_serializer = OrderSerializer(pending,  many=True)
    previous_serializer = OrderSerializer(previous,  many=True)
    return Response(data={"pending": pending_serializer.data, "previous": previous_serializer.data}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_previous_orders(request: Request):
    page = int(request.query_params.get("page"))
    search_text = request.query_params.get("search_text")
    filter_query = {"user": request.user, "order_status__name__in": [
        "Delivered", "Undelivered", "Rejected"]}
    if search_text != "" and len(search_text) >= 3:
        filter_query.update(
            {"cart__product_quantity__product__display_name__icontains": search_text})
    orders = Order.objects.prefetch_related("orderfeedback_set").filter(
        **filter_query).select_related("order_status", "payment_mode", "user").annotate(
        has_feedback=Case(When(orderfeedback__isnull=False, then=Value(True)), default=Value(False), output_field=BooleanField(),)).distinct()[(6*page)-6: 6*page]
    serializer = OrderSerializer(orders,  many=True)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_order_feedback(request: Request):
    try:
        feedback_list = []
        order_id = int(request.data.get("order").split("#")[1])
        product_dict = {product.name: product for product in Product.objects.filter(
            name__in=[name for name in request.data.get("item_feedbacks")])}
        vendor_dict = {vendor.display_name: vendor for vendor in Vendor.objects.filter(
            display_name__in=[name for name in request.data.get("vendor_feedbacks")])}

        # Create OrderFeedback objects for products
        for key in product_dict:
            feedback_list.append(
                OrderFeedback(
                    content_object=product_dict[key],
                    user=request.user,
                    order_id=order_id,
                    rating=int(request.data["item_feedbacks"][key]["rating"]),
                    comment=request.data["item_feedbacks"][key]["comment"],
                )
            )

        # Create OrderFeedback objects for vendors
        for key in vendor_dict:
            feedback_list.append(
                OrderFeedback(
                    content_object=vendor_dict[key],
                    user=request.user,
                    order_id=order_id,
                    rating=int(
                        request.data["vendor_feedbacks"][key]["rating"]),
                    comment=request.data["vendor_feedbacks"][key]["comment"],
                )
            )

        # Insert OrderFeedback entries
        OrderFeedback.objects.bulk_create(feedback_list)
        return Response(data={"details": "Thank you for submitting your feedback"}, status=status.HTTP_200_OK)

    except (IndexError, ValueError):
        return Response(data={"details": "Could not fetch order details from request"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response(data={"details": "Error occured while submitting feedback"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
