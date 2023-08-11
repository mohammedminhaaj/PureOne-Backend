from django.contrib import admin
from .models import Order
from common.admin import AuditedAdminMixin

# Register your models here.
@admin.register(Order)
class OrderAdmin(AuditedAdminMixin):
    list_display = ['order_id', 'user', 'order_status', 'payment_mode','amount', 'long_address', 'building', 'locality', 'landmark']