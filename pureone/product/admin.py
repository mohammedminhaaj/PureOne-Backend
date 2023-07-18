from django.contrib import admin
from .models import Category, Product, Quantity, ProductQuantity, Cart
from common.admin import AuditedAdminMixin

from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory

ProductQuantityFormFormSet = inlineformset_factory(Product, ProductQuantity, fields=(
    'quantity', 'price', 'original_price'), extra=1, formset=BaseInlineFormSet)

class ProductQuantityInline(admin.TabularInline):
    model = ProductQuantity
    formset = ProductQuantityFormFormSet

# Register your models here.
@admin.register(Category)
class CategoryAdmin(AuditedAdminMixin):
    list_display = ['name', 'display_name']

@admin.register(Quantity)
class QuantityAdmin(AuditedAdminMixin):
    list_display = ['grams', 'display_name']

@admin.register(Product)
class ProductAdmin(AuditedAdminMixin):
    prepopulated_fields = {'name': ('display_name',)}
    list_display = ['vendor', 'display_name', 'name', 'category', 'is_featured', 'available_quantity']
    inlines = [ProductQuantityInline]

@admin.register(ProductQuantity)
class ProductQuantityAdmin(AuditedAdminMixin):
    list_display = ['product', 'quantity', 'price', 'original_price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'product_quantity', 'created_at', 'modified_at']