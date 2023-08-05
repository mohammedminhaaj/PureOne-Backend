from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv
from os import getenv

def haversine(latitude: float, longitude: float, coordinate_list: list[tuple[float]]) -> list[tuple[float]] | list[None]:
    load_dotenv()
    RADIUS_TO_SEARCH = getenv("RADIUS_KMS")
    EARTH_RADIUS_KM = 6371.0 #constant for haversine formula
    within_km = []
    try:
        current_latitude = radians(float(latitude))
        current_longitude = radians(float(longitude))
    except ValueError:
        return within_km

    
    for coordinate in coordinate_list:
        lt = radians(coordinate[0])
        ln = radians(coordinate[1])

        # Using the Haversine formula to calculate distance
        d_latitude = lt - current_latitude
        d_longitude = ln - current_longitude

        a = sin(d_latitude / 2) ** 2 + cos(current_latitude) * cos(lt) * sin(d_longitude / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = EARTH_RADIUS_KM * c

        if distance <= int(RADIUS_TO_SEARCH):
            within_km.append(coordinate)

    return within_km
    
