from django.contrib import admin
from .models import Cart, Coupon, CouponRedemption

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_quantity', 'quantity_count', 'order', 'order_price', 'created_at', 'modified_at']

    def get_queryset(self, request):
        queryset = Cart.all_objects.select_related("user", "product_quantity", "order")
        return queryset
    
admin.site.register(CouponRedemption)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'description', 'coupon_type', 'discount_percentage', 'discount_amount', 'max_discount_amount', 'min_order_amount', 'valid_from', 'valid_until', 'usage_limit', 'is_active']
