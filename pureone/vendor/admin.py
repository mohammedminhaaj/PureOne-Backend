from django.contrib import admin
from .models import Region, Vendor
from common.admin import AuditedAdminMixin
# Register your models here.
@admin.register(Region)
class RegionAdmin(AuditedAdminMixin):
    list_display = ['name', 'display_name']

@admin.register(Vendor)
class VendorAdmin(AuditedAdminMixin):
    prepopulated_fields = {'name': ('display_name',)}
    list_display = ['display_name','name', 'region']