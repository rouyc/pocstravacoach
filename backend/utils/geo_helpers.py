import math
from typing import List, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance entre deux points GPS en kilomètres
    Utilise la formule de Haversine

    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point

    Returns:
        Distance en kilomètres
    """
    R = 6371  # Rayon de la Terre en km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon / 2) ** 2

    c = 2 * math.asin(math.sqrt(a))

    return R * c


def calculate_total_distance(coordinates: List[Tuple[float, float]]) -> float:
    """
    Calcule la distance totale d'un parcours

    Args:
        coordinates: Liste de tuples (lat, lon)

    Returns:
        Distance totale en kilomètres
    """
    if len(coordinates) < 2:
        return 0.0

    total_distance = 0.0
    for i in range(len(coordinates) - 1):
        lat1, lon1 = coordinates[i]
        lat2, lon2 = coordinates[i + 1]
        total_distance += haversine_distance(lat1, lon1, lat2, lon2)

    return total_distance


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule le cap (bearing) entre deux points GPS

    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point

    Returns:
        Cap en degrés (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)

    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360

    return bearing


def destination_point(lat: float, lon: float, distance_km: float, bearing: float) -> Tuple[float, float]:
    """
    Calcule le point de destination à partir d'un point de départ,
    d'une distance et d'un cap

    Args:
        lat, lon: Coordonnées du point de départ
        distance_km: Distance en kilomètres
        bearing: Cap en degrés

    Returns:
        Tuple (latitude, longitude) du point d'arrivée
    """
    R = 6371  # Rayon de la Terre en km

    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    bearing_rad = math.radians(bearing)

    lat2_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance_km / R) +
        math.cos(lat_rad) * math.sin(distance_km / R) * math.cos(bearing_rad)
    )

    lon2_rad = lon_rad + math.atan2(
        math.sin(bearing_rad) * math.sin(distance_km / R) * math.cos(lat_rad),
        math.cos(distance_km / R) - math.sin(lat_rad) * math.sin(lat2_rad)
    )

    return math.degrees(lat2_rad), math.degrees(lon2_rad)


def coordinates_to_geojson(coordinates: List[Tuple[float, float]]) -> dict:
    """
    Convertit une liste de coordonnées en GeoJSON LineString

    Args:
        coordinates: Liste de tuples (lat, lon)

    Returns:
        Objet GeoJSON
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat] for lat, lon in coordinates]  # GeoJSON utilise [lon, lat]
                },
                "properties": {}
            }
        ]
    }
