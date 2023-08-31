from .models import OrderFeedback
from django.db.models import Avg, OuterRef
from django.contrib.contenttypes.models import ContentType
from typing import Any

def get_average_rating(content_type: ContentType):
    return OrderFeedback.objects.filter(
        content_type=content_type,
        object_id=OuterRef("pk")
    ).values("object_id").annotate(
        avg_rating=Avg("rating")
    ).values("avg_rating")[:1]