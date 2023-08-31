from rest_framework import serializers
from vendor.models import Vendor
from common.utils import haversine
from math import radians, ceil


class VendorSerializer(serializers.ModelSerializer):
    vendor_status = serializers.CharField(source="vendor_status.display_name")

    class Meta:
        model = Vendor
        fields = ["display_name", "latitude", "longitude",
                  "address", "vendor_status", "contact"]


class NearbyVendorSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.current_latitude = kwargs.pop("current_latitude")
        self.current_longitude = kwargs.pop("current_longitude")
        super().__init__(*args, **kwargs)

    def get_rating(self, obj):
        return obj.average_rating

    def get_distance(self, obj):
        distance = haversine(radians(self.current_latitude), radians(self.current_longitude), obj.latitude, obj.longitude)
        return ceil(distance)

    class Meta:
        model = Vendor
        fields = ["display_name", "rating", "distance"]
