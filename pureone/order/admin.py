from django.contrib import admin
from .models import Order, OrderFeedback
from common.admin import AuditedAdminMixin

# Register your models here.
@admin.register(Order)
class OrderAdmin(AuditedAdminMixin):
    list_display = ['order_id', 'user', 'order_status', 'payment_mode','amount', 'delivery_charge', 'discount','long_address', 'building', 'locality', 'landmark', "delivered_at"]

@admin.register(OrderFeedback)
class OrderFeedbackAdmin(AuditedAdminMixin):
    list_display = ["content_object", "user", "order", "rating", "comment"]