from django.contrib import admin
from ..models import MasterCategory, MasterData, PromotionalBanner
from .base import AuditedAdminMixin
# Register your models here.

@admin.register(MasterCategory)
class MasterCategoryAdmin(AuditedAdminMixin):
    list_display = ['name', 'display_name']

@admin.register(MasterData)
class MasterDataAdmin(AuditedAdminMixin):
    list_display = ['master_category' ,'name', 'display_name']

@admin.register(PromotionalBanner)
class PromotionalBannerAdmin(AuditedAdminMixin):
    list_display = ['name' ,'description', 'banner']
