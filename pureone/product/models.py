from django.db import models
from common.models.base import AuditedModel, SoftDeleteModel
from common.models.managers import SoftDeleteManager, RestorableManager
from django.utils.translation import gettext_lazy as _
from vendor.models import Vendor
from django.contrib.contenttypes.fields import GenericRelation

# Create your models here.


class Category(AuditedModel, SoftDeleteModel):
    name = models.CharField(max_length=32)
    display_name = models.CharField(max_length=32)
    image = models.ImageField(verbose_name=_("Image"), upload_to="categories")

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        db_table = 'category'
        ordering = ['name']


class Quantity(AuditedModel, SoftDeleteModel):
    grams = models.PositiveIntegerField()
    display_name = models.CharField(max_length=32)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Quantity'
        verbose_name_plural = 'Quantities'
        db_table = 'quantity'
        ordering = ['grams']


class Product(AuditedModel, SoftDeleteModel):
    display_name = models.CharField(max_length=128)
    name = models.CharField(db_index=True, max_length=128, unique=True)
    description = models.TextField(max_length=1024)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.CharField(max_length=1024, help_text=_(
        "Use comma (,) to separate each tag."))
    is_featured = models.BooleanField(
        default=False, verbose_name=_("Is Featured?"))
    image = models.ImageField(verbose_name=_("Image"), upload_to="products")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    product_quantity = models.ManyToManyField(Quantity, through="ProductQuantity", through_fields=(
        "product", "quantity"), verbose_name=_("Product Quantity"))
    available_quantity = models.PositiveIntegerField(
        verbose_name=_("Available Quantity"))
    feedback = GenericRelation("order.OrderFeedback", related_query_name="product_feedback")

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'product'
        ordering = ['-id']


class ProductQuantity(AuditedModel, SoftDeleteModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.ForeignKey(Quantity, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    original_price = models.DecimalField(max_digits=7, decimal_places=2)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return f"{self.product} - {self.quantity.display_name}"

    class Meta:
        verbose_name = 'Product Quantity'
        verbose_name_plural = 'Product Quantities'
        db_table = 'product_quantity'
        ordering = ['quantity__grams']
        constraints = [models.UniqueConstraint(
            fields=("product", "quantity"), name="unique_product_quantity_mapping")]


