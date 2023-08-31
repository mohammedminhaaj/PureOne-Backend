from django.db import connection
from rest_framework import status
from .models import Coupon, CouponRedemption
from user.models import User
from common import constants
from decimal import Decimal


class CouponError(Exception):
    '''
    Custom exception for coupon errors
    '''

    def __init__(self, message: str, status: int | None = None) -> None:
        self.status = status
        self.message = message
        super().__init__(self.message)

def get_delivery_charge() -> Decimal:
    '''
    Helper function to get the delivery charge from MySQL Function 
    '''
    with connection.cursor() as cursor:
        cursor.execute('SELECT calculate_delivery_charge()')
        result = cursor.fetchone()
    return Decimal(result[0])

def validate_coupon(user: User, coupon_code: str | None = None) -> Coupon:
    '''
    Helper function to validate coupon code

    '''

    if not coupon_code:
        raise CouponError(message="Error occured while getting coupon code.", status = status.HTTP_400_BAD_REQUEST)
    
    try:
        coupon = Coupon.objects.select_related("coupon_type").get(code__iexact = coupon_code)
        if not coupon.is_active:
           raise Coupon.DoesNotExist
        if not coupon.is_available:
            raise CouponError(message="Coupon expired!", status = status.HTTP_404_NOT_FOUND)
        
        coupon_redemption_count = CouponRedemption.objects.filter(user = user, coupon = coupon).count()
        if coupon_redemption_count >= coupon.usage_limit:
            raise CouponError(message="Maximum limit reached!", status = status.HTTP_400_BAD_REQUEST)
        
        return coupon
        
    except Coupon.DoesNotExist:
        raise CouponError(message="Invalid coupon code!", status = status.HTTP_400_BAD_REQUEST)
    except CouponError as e:
        raise CouponError(message=e.message, status=e.status)
    except Exception:
        raise CouponError(message=constants.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def get_discount_amount(coupon: Coupon, amount: Decimal, delivery_charge: Decimal) -> Decimal:
    # Calculate the total
    total = amount + delivery_charge

    # Check if the minimun order amount value is present in the coupon
    # If so, check whether the total is less than minimun order amount
    if coupon.min_order_amount and total < coupon.min_order_amount:
        raise CouponError(message="Total is not less than minimum order amount", status= status.HTTP_400_BAD_REQUEST)
    
    match coupon.coupon_type.name:
        case "Fixed Amount":
            if not coupon.discount_amount:
                return Decimal(0.0)
            return coupon.discount_amount
        case "Free Shipping":
            return delivery_charge
        case "Percentage":
            if not coupon.discount_percentage:
                return Decimal(0.0)
            discount_amount = amount * (coupon.discount_percentage/Decimal(100.0))
            if coupon.max_discount_amount:
                return discount_amount if discount_amount <= coupon.max_discount_amount else coupon.max_discount_amount
            else:
                return discount_amount
        case _:
            raise CouponError(message="Coupon type not defined", status= status.HTTP_404_NOT_FOUND)
    

    

    
