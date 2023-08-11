from rest_framework import serializers
from vendor.models import Vendor

class VendorSerializer(serializers.ModelSerializer):
    vendor_status = serializers.CharField(source = "vendor_status.display_name")
    class Meta:
        model = Vendor
        fields = ["display_name", "latitude", "longitude", "address", "vendor_status", "contact"]