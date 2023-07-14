from django.db import models
from .base import AuditedModel, SoftDeleteModel
from .managers import SoftDeleteManager, RestorableManager
from django.utils.translation import gettext_lazy as _

# Create your models here.
class MasterCategory(AuditedModel, SoftDeleteModel):
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length = 64)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Master Category'
        verbose_name_plural = 'Master Categories'
        db_table = 'master_category'
        ordering = ['name']

class MasterData(AuditedModel, SoftDeleteModel):
    master_category = models.ForeignKey(MasterCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    display_name = models.CharField(max_length = 64)

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.display_name

    class Meta:
        verbose_name = 'Master Data'
        verbose_name_plural = 'Master Data'
        db_table = 'master_data'
        ordering = ['name']


class PromotionalBanner(AuditedModel, SoftDeleteModel):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=512, null=True, blank=True)
    banner = models.ImageField(verbose_name=_("Banner"), upload_to="banners")

    objects = SoftDeleteManager()
    all_objects = RestorableManager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Promotional Banner'
        verbose_name_plural = 'Promotional Banners'
        db_table = 'promotional_banner'
        ordering = ['name']