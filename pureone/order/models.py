from django.db import models

# Create your models here.
from common.models.base import AuditedModel, SoftDeleteModel
from common.models.managers import SoftDeleteManager, RestorableManager
from django.utils.translation import gettext_lazy as _
from common.models import MasterData
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Order(AuditedModel, SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_status = models.ForeignKey(MasterData, on_delete=models.CASCADE, verbose_name=_("Order Status"), limit_choices_to=models.Q(master_category__name = "Order Status"), related_name="md_order_status")
    payment_mode = models.ForeignKey(MasterData, on_delete=models.CASCADE, verbose_name=_("Payment Mode"), limit_choices_to=models.Q(master_category__name = "Payment Mode"), related_name="md_payment_mode")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    latitude = models.DecimalField(max_digits=19, decimal_places=16)
    longitude = models.DecimalField(max_digits=19, decimal_places=16)
    short_address = models.CharField(max_length = 256, verbose_name=_("Short Address"))
    long_address = models.CharField(max_length = 512, verbose_name=_("Long Address"))
    building = models.CharField(max_length = 64, blank = True, null=True)
    locality = models.CharField(max_length = 64, blank = True, null=True)
    landmark = models.CharField(max_length = 64, blank = True, null=True)
    delivery_instructions = models.TextField(max_length=150, verbose_name=_("Delivery Instructions"), null = True, blank = True)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    @property
    def order_id(self):
        return f"Order #{self.id:07d}"
    
    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f"user_{self.user.id}_order_list", {"type": "order_status", "order_id": self.order_id, "status": self.order_status.display_name})
        return instance

    def __str__(self) -> str:
        return self.order_id

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        db_table = 'order'
        ordering = ['-id']