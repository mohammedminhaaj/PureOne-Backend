from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv
from os import getenv
from vendor.models import Vendor
from typing import Iterable, Any

EARTH_RADIUS_KM = 6371.0 #constant for haversine formula

def haversine(current_latitude: Any, current_longitude: Any, target_latitude: Any, target_longitude: Any) -> float :
    lt = radians(target_latitude)
    ln = radians(target_longitude)

    # Using the Haversine formula to calculate distance
    d_latitude = lt - current_latitude
    d_longitude = ln - current_longitude

    a = sin(d_latitude / 2) ** 2 + cos(current_latitude) * cos(lt) * sin(d_longitude / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS_KM * c

def get_nearby_vendors(latitude: float, longitude: float, vendors: Iterable) -> list[Vendor] | list[None]:
    load_dotenv()
    RADIUS_TO_SEARCH = getenv("RADIUS_KMS")
    within_km = []
    try:
        current_latitude = radians(latitude)
        current_longitude = radians(longitude)
    except ValueError:
        return within_km

    for vendor in vendors:
        distance = haversine(current_latitude, current_longitude, vendor.latitude, vendor.longitude)

        if distance <= int(RADIUS_TO_SEARCH):
            within_km.append(vendor)

    return within_km
    
