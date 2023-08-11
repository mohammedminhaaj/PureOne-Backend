from django.contrib import admin
from .models import Cart

# Register your models here.
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_quantity', 'quantity_count','order', 'created_at', 'modified_at']

    def get_queryset(self, request):
        queryset = Cart.all_objects.select_related("user", "product_quantity", "order")
        return queryset