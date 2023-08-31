from django.db import models

# Create your models here.
from common.models.base import AuditedModel, SoftDeleteModel
from common.models.managers import SoftDeleteManager, RestorableManager
from django.utils.translation import gettext_lazy as _
from common.models import MasterData
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator

def get_order_body(order_status: str) -> str:
    match order_status:
        case "Accepted":
            return "Your order has been accepted. We will let you know as soon as it get's dispatched."
        case "Dispatched":
            return "Your order is on it's way and will be arriving at your doorstep soon. Thank you for your patience."
        case "Delivered":
            return "Your order has been delivered. Please take a few minutes of your time to provide us the feedback. Your feedback is valuable to us as it will help us improve the product and overall user exeprience."
        case "Rejected":
            return "We are sorry to inform you that your order has been rejected by the vendor."
        case "Undelivered":
            return "Your order couldn't be delivered."
        case _:
            return "Your order has been updated"

class Order(AuditedModel, SoftDeleteModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_status = models.ForeignKey(MasterData, on_delete=models.CASCADE, verbose_name=_("Order Status"), limit_choices_to=models.Q(master_category__name = "Order Status"), related_name="md_order_status")
    payment_mode = models.ForeignKey(MasterData, on_delete=models.CASCADE, verbose_name=_("Payment Mode"), limit_choices_to=models.Q(master_category__name = "Payment Mode"), related_name="md_payment_mode")
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    delivery_charge = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=7, decimal_places=2, default=0.0, null=True, blank = True)
    latitude = models.DecimalField(max_digits=19, decimal_places=16)
    longitude = models.DecimalField(max_digits=19, decimal_places=16)
    short_address = models.CharField(max_length = 256, verbose_name=_("Short Address"))
    long_address = models.CharField(max_length = 512, verbose_name=_("Long Address"))
    building = models.CharField(max_length = 64, blank = True, null=True)
    locality = models.CharField(max_length = 64, blank = True, null=True)
    landmark = models.CharField(max_length = 64, blank = True, null=True)
    delivery_instructions = models.TextField(max_length=150, verbose_name=_("Delivery Instructions"), null = True, blank = True)
    delivered_at = models.DateTimeField(verbose_name=_("Delivered At"), null = True, blank = True, editable=False)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    @property
    def order_id(self):
        return f"Order #{self.id:07d}"
    
    @property
    def total(self):
        total = self.amount + self.delivery_charge
        if self.discount:
            total -= self.discount
        return total
    
    def save(self, *args, **kwargs):
        #Set the delivered_at field to current time
        if self.order_status and self.order_status.name == "Delivered":
            self.delivered_at = now()

        instance = super().save(*args, **kwargs)
        if self.pk:
            #To update the screen whenever order is modified
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(f"user_{self.user.id}_order_list", {"type": "order_status", "order_id": self.order_id, "status": self.order_status.display_name})

            #To send push notification when the user is not using the app
            devices = FCMDevice.objects.filter(user = self.user)

            devices.send_message(message=Message(notification=Notification(title=f"{self.order_id}", body=get_order_body(self.order_status.name))))

        return instance

    def __str__(self) -> str:
        return self.order_id

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        db_table = 'order'
        ordering = ['-id']

class OrderFeedback(AuditedModel, SoftDeleteModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1, message=_("Rating cannot be less than 1")), MaxValueValidator(5, message=_("Rating cannot be greater than 5"))])
    comment = models.TextField(max_length=150, blank = True, null = True)

    def __str__(self) -> str:
        return f"Feedback for {self.order.order_id} - {self.content_type.model}"

    class Meta:
        verbose_name = 'Order Feedback'
        verbose_name_plural = 'Order Feedbacks'
        db_table = 'order_feedback'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(fields=(
                "content_type", "object_id", "user", "order"), name="unique_content_type_object_user_order_mapping"),
        ]