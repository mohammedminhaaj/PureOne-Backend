from django.db import models
from common.models.managers import CartManager, RestorableManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from product.models import ProductQuantity
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