from django.db import models
from common.models.base import AuditedModel, SoftDeleteModel
from common.models.managers import SoftDeleteManager, RestorableManager
from common.models import MasterData
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Create your models here.
class Region(AuditedModel, SoftDeleteModel):
    name = models.CharField(max_length=30)
    display_name = models.CharField(max_length = 30)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'
        db_table = 'region'
        ordering = ['name']

class Vendor(AuditedModel, SoftDeleteModel):
    display_name = models.CharField(max_length = 128)
    name  = models.CharField(max_length = 128)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=19, decimal_places=16)
    longitude = models.DecimalField(max_digits=19, decimal_places=16)
    address = models.TextField(max_length=1024)
    vendor_status = models.ForeignKey(MasterData, on_delete=models.CASCADE, verbose_name=_("Vendor Status"), limit_choices_to=Q(master_category__name = "Vendor Status"))

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        db_table = 'vendor'
        ordering = ['-id']