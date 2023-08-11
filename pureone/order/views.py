from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from cart.models import Cart
from rest_framework import status
from common.models import MasterData
from .models import Order
from common.serializers.order_serializer import OrderSerializer
from cart.helpers import get_delivery_charge
from decimal import Decimal

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
            return Response(data={"details": "One or more items are out of stock. Please refresh."}, status = status.HTTP_400_BAD_REQUEST)
        elif cart.product_quantity.product.vendor.vendor_status.name != "Open":
            return Response(data={"details": "One or more vendors are unserviceable. Please refresh."}, status = status.HTTP_400_BAD_REQUEST)
        
        amount += cart.product_quantity.price * cart.quantity_count

    #Append delivery charges
    amount += Decimal(get_delivery_charge())
        
    # Fire a single query to fetch both records from master data    
    base_qs = MasterData.objects.select_related("master_category").filter(name__in = ["Placed", "Cash"], master_category__name__in = ["Order Status", "Payment Mode"])

    #Generate a dictionary to separate both master data
    base_qs_dict = {qs.name: qs for qs in base_qs}
        
    order_status = base_qs_dict.get("Placed")
    payment_mode = base_qs_dict.get("Cash")

    try:
        #Create the order object
        order = Order.objects.create(
            user = request.user,
            order_status = order_status,
            payment_mode = payment_mode,
            amount = amount,
            latitude = request.data.get("latitude"),
            longitude = request.data.get("longitude"),
            short_address = request.data.get("short_address"),
            long_address = request.data.get("long_address"),
            building = request.data.get("building"),
            locality = request.data.get("locality"),
            landmark = request.data.get("landmark"),
            delivery_instructions = request.data.get("delivery_instructions")
        )

        #update cart objects with the newly created order object
        carts.update(order = order)

        return Response(data={"details": "Order placed"}, status = status.HTTP_201_CREATED)
    except Exception:
        return Response(data={"details": "Error occured while placing order"}, status = status.HTTP_400_BAD_REQUEST)
    

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_orders(request: Request):
    orders = Order.objects.filter(user = request.user).select_related("order_status", "payment_mode", "user")[:8]
    pending = []
    previous = []
    for order in orders:
        if order.order_status.name not in ["Delivered", "Undelivered", "Rejected"]:
            pending.append(order)
        else:
            previous.append(order)
    pending_serializer = OrderSerializer(pending,  many = True)
    previous_serializer = OrderSerializer(previous,  many = True)
    return Response(data={"pending": pending_serializer.data, "previous": previous_serializer.data}, status = status.HTTP_200_OK)