from django.db import models
from common.models.managers import CartManager, RestorableManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from product.models import ProductQuantity
from order.models import Order
from django.utils.timezone import now
from common.models import MasterData
from django.db.models import Q
from order.models import Order

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product_quantity = models.ForeignKey(
        ProductQuantity, on_delete=models.CASCADE)
    quantity_count = models.PositiveIntegerField(default=1, verbose_name=_(
        "Quantity Count"), validators=[MinValueValidator(1, message=_("Quantity count can't be less than 1")), MaxValueValidator(10, message=_("Quantity count can't be greater than 10"))])
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, default=None)
    order_price = models.DecimalField(max_digits=7, decimal_places=2, null= True, blank= True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created At"))
    modified_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Modified At"))

    objects = CartManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return f"{self.user} - {self.product_quantity.product} - {self.product_quantity.quantity}"

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Cart'
        db_table = 'cart'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=(
                "user", "product_quantity", "order"), name="unique_user_product_quantity_mapping"),
        ]


class Coupon(models.Model):    
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(max_length=256)
    coupon_type = models.ForeignKey(MasterData, on_delete=models.CASCADE, limit_choices_to=Q(master_category__name = "Coupon Type"), verbose_name=_("Discount Type"))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Discount Percentage"))
    discount_amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name=_("Discount Amount"))
    max_discount_amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name=_("Maximum Discount Amount"))
    min_order_amount = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, verbose_name=_("Minimum Order Amount"))
    valid_from = models.DateTimeField(verbose_name=_("Valid From"))
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name=_("Valid Until"))
    usage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Usage Limit"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    def __str__(self) -> str:
        return self.code

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        db_table = 'coupon'
        ordering = ['-id']
    
    @property
    def is_available(self):
        return self.valid_from <= now() and (not self.valid_until or (self.valid_until and self.valid_until >= now()))
    
class CouponRedemption(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user} applied {self.coupon} in {self.order}"

    class Meta:
        verbose_name = 'Coupon Redemption'
        verbose_name_plural = 'Coupons Redemptions'
        db_table = 'coupon_redemption'
        ordering = ['-id']
