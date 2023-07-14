from rest_framework import serializers
from common.models import PromotionalBanner

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionalBanner
        fields = ["banner"]