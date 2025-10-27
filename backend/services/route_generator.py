import httpx
import gpxpy
import gpxpy.gpx
from typing import List, Tuple, Optional
from datetime import datetime

from utils.geo_helpers import (
    haversine_distance,
    calculate_total_distance,
    calculate_bearing,
    destination_point,
    coordinates_to_geojson
)
from services.elevation import ElevationService
from models import RouteRequest, ElevationPreference


class RouteGenerator:
    """Service de génération de parcours"""

    def __init__(self, elevation_service: ElevationService):
        self.elevation_service = elevation_service
        # OSRM public instance
        self.osrm_base_url = "https://router.project-osrm.org"

    async def generate_route(
        self,
        start_lat: float,
        start_lon: float,
        request: RouteRequest
    ) -> Tuple[List[Tuple[float, float]], dict, str]:
        """
        Génère un parcours complet

        Args:
            start_lat: Latitude du point de départ
            start_lon: Longitude du point de départ
            request: Paramètres de la requête

        Returns:
            Tuple (coordonnées, métriques, gpx)
        """
        # Pour ce POC, on utilise une approche "aller-retour"
        # On génère un point de destination puis on fait un aller-retour

        # Calculer la distance pour l'aller (la moitié de la distance totale)
        one_way_distance = request.distance_km / 2

        # Générer plusieurs candidats de parcours dans différentes directions
        best_route = None
        best_score = float('inf')

        # Essayer 8 directions différentes (tous les 45 degrés)
        for bearing in range(0, 360, 45):
            route = await self._generate_out_and_back_route(
                start_lat, start_lon, one_way_distance, bearing, request
            )

            if route:
                score = await self._score_route(route, request)
                if score < best_score:
                    best_score = score
                    best_route = route

        if not best_route:
            # Fallback: route simple en ligne droite
            best_route = await self._generate_simple_route(
                start_lat, start_lon, request.distance_km
            )

        # Calculer les métriques
        metrics = await self._calculate_route_metrics(best_route, request.distance_km)

        # Générer le GeoJSON
        geojson = coordinates_to_geojson(best_route)

        # Générer le GPX
        gpx = self._generate_gpx(best_route, request)

        return best_route, metrics, gpx

    async def _generate_out_and_back_route(
        self,
        start_lat: float,
        start_lon: float,
        one_way_distance: float,
        bearing: float,
        request: RouteRequest
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Génère un parcours aller-retour dans une direction donnée

        Args:
            start_lat: Latitude de départ
            start_lon: Longitude de départ
            one_way_distance: Distance de l'aller (en km)
            bearing: Direction en degrés
            request: Paramètres de la requête

        Returns:
            Liste de coordonnées ou None
        """
        # Calculer le point de destination
        dest_lat, dest_lon = destination_point(start_lat, start_lon, one_way_distance, bearing)

        # Construire les profils de routing selon les préférences
        profile = self._get_routing_profile(request)

        # Appeler OSRM pour l'aller
        outbound_coords = await self._get_osrm_route(
            start_lat, start_lon, dest_lat, dest_lon, profile
        )

        if not outbound_coords:
            return None

        # Pour le retour, inverser le trajet
        inbound_coords = list(reversed(outbound_coords))

        # Combiner aller + retour
        full_route = outbound_coords + inbound_coords[1:]  # Éviter de dupliquer le point de retournement

        return full_route

    async def _generate_simple_route(
        self,
        start_lat: float,
        start_lon: float,
        distance_km: float
    ) -> List[Tuple[float, float]]:
        """
        Génère une route simple en ligne droite (fallback)

        Args:
            start_lat: Latitude de départ
            start_lon: Longitude de départ
            distance_km: Distance totale

        Returns:
            Liste de coordonnées
        """
        num_points = 50
        one_way_distance = distance_km / 2
        bearing = 90  # Direction Est

        coords = [(start_lat, start_lon)]

        # Aller
        for i in range(1, num_points // 2):
            dist = (i / (num_points // 2)) * one_way_distance
            lat, lon = destination_point(start_lat, start_lon, dist, bearing)
            coords.append((lat, lon))

        # Point le plus éloigné
        end_lat, end_lon = destination_point(start_lat, start_lon, one_way_distance, bearing)
        coords.append((end_lat, end_lon))

        # Retour
        for i in range(num_points // 2 - 1, 0, -1):
            dist = (i / (num_points // 2)) * one_way_distance
            lat, lon = destination_point(start_lat, start_lon, dist, bearing)
            coords.append((lat, lon))

        coords.append((start_lat, start_lon))

        return coords

    async def _get_osrm_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        profile: str = "foot"
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Appelle OSRM pour obtenir un itinéraire

        Args:
            start_lat, start_lon: Point de départ
            end_lat, end_lon: Point d'arrivée
            profile: Profil de routing (foot, bike, car)

        Returns:
            Liste de coordonnées ou None
        """
        url = f"{self.osrm_base_url}/route/v1/{profile}/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()

                data = response.json()

                if data["code"] != "Ok" or not data.get("routes"):
                    return None

                # Extraire les coordonnées de la géométrie
                geometry = data["routes"][0]["geometry"]
                coordinates = geometry["coordinates"]

                # Convertir de [lon, lat] à (lat, lon)
                route_coords = [(lat, lon) for lon, lat in coordinates]

                return route_coords

            except Exception as e:
                print(f"Erreur OSRM: {e}")
                return None

    def _get_routing_profile(self, request: RouteRequest) -> str:
        """
        Détermine le profil de routing selon les préférences

        Args:
            request: Paramètres de la requête

        Returns:
            Nom du profil OSRM
        """
        # Pour ce POC, on utilise toujours "foot" (marche/course)
        # En production, on pourrait ajouter "bike" pour le vélo
        return "foot"

    async def _score_route(
        self,
        coordinates: List[Tuple[float, float]],
        request: RouteRequest
    ) -> float:
        """
        Calcule un score pour évaluer la qualité d'un parcours
        Plus le score est bas, meilleur est le parcours

        Args:
            coordinates: Coordonnées du parcours
            request: Paramètres de la requête

        Returns:
            Score (plus bas = meilleur)
        """
        score = 0.0

        # 1. Pénalité pour écart de distance
        actual_distance = calculate_total_distance(coordinates)
        distance_diff = abs(actual_distance - request.distance_km)
        score += distance_diff * 10  # Forte pénalité pour écart de distance

        # 2. Pénalité pour dénivelé non conforme
        elevations = await self.elevation_service.get_elevations(coordinates)
        elevation_gain, _ = self.elevation_service.calculate_elevation_metrics(elevations)

        if not self.elevation_service.matches_elevation_preference(
            elevation_gain, actual_distance, request.elevation_preference.value
        ):
            score += 50  # Pénalité si le dénivelé ne correspond pas

        return score

    async def _calculate_route_metrics(
        self,
        coordinates: List[Tuple[float, float]],
        target_distance: float
    ) -> dict:
        """
        Calcule les métriques du parcours

        Args:
            coordinates: Coordonnées du parcours
            target_distance: Distance cible

        Returns:
            Dictionnaire de métriques
        """
        actual_distance = calculate_total_distance(coordinates)

        # Récupérer les élévations
        elevations = await self.elevation_service.get_elevations(coordinates)
        elevation_gain, elevation_loss = self.elevation_service.calculate_elevation_metrics(elevations)

        # Estimer la durée (hypothèse: 5 min/km en course)
        estimated_duration = int(actual_distance * 5)

        return {
            "distance_km": round(actual_distance, 2),
            "elevation_gain_m": round(elevation_gain, 1),
            "elevation_loss_m": round(elevation_loss, 1),
            "estimated_duration_min": estimated_duration
        }

    def _generate_gpx(
        self,
        coordinates: List[Tuple[float, float]],
        request: RouteRequest
    ) -> str:
        """
        Génère un fichier GPX à partir des coordonnées

        Args:
            coordinates: Liste de coordonnées
            request: Paramètres de la requête

        Returns:
            Contenu GPX au format string
        """
        gpx = gpxpy.gpx.GPX()

        # Métadonnées
        gpx.name = f"Parcours {request.training_type.value} - {request.distance_km}km"
        gpx.description = f"Généré par Strava+Coach - Dénivelé: {request.elevation_preference.value}"
        gpx.creator = "Strava+Coach POC"

        # Créer un track
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        # Créer un segment
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Ajouter les points
        for lat, lon in coordinates:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lon))

        return gpx.to_xml()
