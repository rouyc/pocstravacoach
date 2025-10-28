import httpx
import gpxpy
import gpxpy.gpx
import logging
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
from models import RouteRequest, ElevationPreference, RouteType

# Configuration du logger
logger = logging.getLogger(__name__)


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
        # Générer plusieurs candidats de parcours dans différentes directions
        best_route = None
        best_score = float('inf')

        # Choisir la méthode de génération selon le type de parcours
        if request.route_type == RouteType.LOOP:
            logger.info("Génération d'un parcours en boucle")
            # Essayer 8 directions différentes pour les boucles
            for bearing in range(0, 360, 45):
                route = await self._generate_loop_route(
                    start_lat, start_lon, request.distance_km, bearing, request
                )

                if route:
                    score = await self._score_route(route, request)
                    if score < best_score:
                        best_score = score
                        best_route = route
        else:  # OUT_AND_BACK ou BOTH (pour l'instant on traite BOTH comme OUT_AND_BACK)
            logger.info("Génération d'un parcours aller-retour")
            # Calculer la distance pour l'aller (la moitié de la distance totale)
            one_way_distance = request.distance_km / 2

            # Essayer 8 directions différentes
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

    async def _generate_loop_route(
        self,
        start_lat: float,
        start_lon: float,
        total_distance: float,
        initial_bearing: float,
        request: RouteRequest
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Génère un parcours en boucle avec ajustement de distance

        Stratégie: Créer 3 points intermédiaires formant un triangle/quadrilatère
        pour revenir au point de départ

        Args:
            start_lat: Latitude de départ
            start_lon: Longitude de départ
            total_distance: Distance totale cible (en km)
            initial_bearing: Direction initiale en degrés
            request: Paramètres de la requête

        Returns:
            Liste de coordonnées ou None
        """
        target_total_distance = total_distance
        tolerance = target_total_distance * 0.02  # ±2%
        max_iterations = 10

        # Facteur initial pour les segments de boucle
        adjustment_factor = 0.80  # Commencer à 80% car les routes réelles sont plus longues

        best_route = None
        best_distance_diff = float('inf')

        for iteration in range(max_iterations):
            # Créer 3 points intermédiaires pour former une boucle
            segment_distance = (total_distance * adjustment_factor) / 3

            # Point 1: direction initiale
            bearing1 = initial_bearing
            point1_lat, point1_lon = destination_point(start_lat, start_lon, segment_distance, bearing1)

            # Point 2: 120° plus loin (pour former un triangle)
            bearing2 = (initial_bearing + 120) % 360
            point2_lat, point2_lon = destination_point(point1_lat, point1_lon, segment_distance, bearing2)

            # Point 3: encore 120° pour revenir vers le départ
            bearing3 = (initial_bearing + 240) % 360
            point3_lat, point3_lon = destination_point(point2_lat, point2_lon, segment_distance, bearing3)

            # Obtenir les profils de routing
            profile = self._get_routing_profile(request)

            # Segment 1: départ -> point1
            seg1 = await self._get_osrm_route(start_lat, start_lon, point1_lat, point1_lon, profile)
            if not seg1:
                continue

            # Segment 2: point1 -> point2
            seg2 = await self._get_osrm_route(point1_lat, point1_lon, point2_lat, point2_lon, profile)
            if not seg2:
                continue

            # Segment 3: point2 -> point3
            seg3 = await self._get_osrm_route(point2_lat, point2_lon, point3_lat, point3_lon, profile)
            if not seg3:
                continue

            # Segment 4: point3 -> retour au départ
            seg4 = await self._get_osrm_route(point3_lat, point3_lon, start_lat, start_lon, profile)
            if not seg4:
                continue

            # Combiner tous les segments en évitant les doublons
            full_route = seg1 + seg2[1:] + seg3[1:] + seg4[1:]

            # Calculer la distance réelle
            actual_distance = calculate_total_distance(full_route)
            distance_diff = abs(actual_distance - target_total_distance)

            # Vérifier que la boucle se ferme bien (tolérance 50m)
            final_point = full_route[-1]
            distance_to_start = haversine_distance(
                start_lat, start_lon, final_point[0], final_point[1]
            )

            # Logger
            logger.info(f"[Loop {initial_bearing}°] Iteration {iteration + 1}: factor={adjustment_factor:.3f}, "
                       f"target={target_total_distance:.2f}km, actual={actual_distance:.2f}km, "
                       f"diff={distance_diff:.2f}km, closure={distance_to_start*1000:.0f}m")

            # Pénalité si la boucle ne se ferme pas bien
            if distance_to_start > 0.05:  # Plus de 50m d'écart
                logger.warning(f"[Loop {initial_bearing}°] Boucle mal fermée: {distance_to_start*1000:.0f}m")
                # On continue quand même mais avec une pénalité
                distance_diff += distance_to_start * 10  # Pénalité

            # Garder la meilleure route
            if distance_diff < best_distance_diff:
                best_distance_diff = distance_diff
                best_route = full_route

            # Vérifier si on est dans la tolérance
            if distance_diff <= tolerance and distance_to_start <= 0.05:
                logger.info(f"OK [Loop {initial_bearing}°] Boucle cible atteinte en {iteration + 1} iteration(s)")
                return full_route

            # Ajuster le facteur
            if actual_distance > target_total_distance:
                adjustment_factor *= 0.95
            else:
                adjustment_factor *= 1.05

            adjustment_factor = max(0.5, min(1.2, adjustment_factor))

        # Retourner la meilleure route trouvée
        if best_route:
            logger.warning(f"WARNING [Loop {initial_bearing}°] Boucle cible non atteinte apres {max_iterations} iterations. "
                          f"Meilleur resultat: ecart de {best_distance_diff:.2f}km")
            return best_route

        return None

    async def _generate_out_and_back_route(
        self,
        start_lat: float,
        start_lon: float,
        one_way_distance: float,
        bearing: float,
        request: RouteRequest
    ) -> Optional[List[Tuple[float, float]]]:
        """
        Génère un parcours aller-retour dans une direction donnée avec ajustement de distance

        Args:
            start_lat: Latitude de départ
            start_lon: Longitude de départ
            one_way_distance: Distance de l'aller (en km)
            bearing: Direction en degrés
            request: Paramètres de la requête

        Returns:
            Liste de coordonnées ou None
        """
        # Algorithme itératif pour atteindre la distance cible avec précision ±2%
        target_total_distance = request.distance_km
        tolerance = target_total_distance * 0.02  # ±2%
        max_iterations = 10

        # Facteur initial : commencer avec 85% de la distance demandée
        # (car les routes réelles sont plus longues que la ligne droite)
        adjustment_factor = 0.85

        best_route = None
        best_distance_diff = float('inf')

        for iteration in range(max_iterations):
            # Calculer la distance ajustée pour cet essai
            adjusted_one_way = one_way_distance * adjustment_factor

            # Calculer le point de destination
            dest_lat, dest_lon = destination_point(start_lat, start_lon, adjusted_one_way, bearing)

            # Construire les profils de routing selon les préférences
            profile = self._get_routing_profile(request)

            # Appeler OSRM pour l'aller
            outbound_coords = await self._get_osrm_route(
                start_lat, start_lon, dest_lat, dest_lon, profile
            )

            if not outbound_coords:
                continue

            # Pour le retour, inverser le trajet
            inbound_coords = list(reversed(outbound_coords))

            # Combiner aller + retour
            full_route = outbound_coords + inbound_coords[1:]  # Éviter de dupliquer le point de retournement

            # Calculer la distance réelle du parcours complet
            actual_distance = calculate_total_distance(full_route)
            distance_diff = abs(actual_distance - target_total_distance)

            # Logger pour debugging
            logger.info(f"[Bearing {bearing}°] Iteration {iteration + 1}: factor={adjustment_factor:.3f}, "
                       f"target={target_total_distance:.2f}km, actual={actual_distance:.2f}km, "
                       f"diff={distance_diff:.2f}km")

            # Garder la meilleure route trouvée
            if distance_diff < best_distance_diff:
                best_distance_diff = distance_diff
                best_route = full_route

            # Vérifier si on est dans la tolérance
            if distance_diff <= tolerance:
                logger.info(f"OK [Bearing {bearing}°] Distance cible atteinte en {iteration + 1} iteration(s)")
                return full_route

            # Ajuster le facteur pour la prochaine itération
            if actual_distance > target_total_distance:
                # Route trop longue, réduire la distance
                adjustment_factor *= 0.95
            else:
                # Route trop courte, augmenter la distance
                adjustment_factor *= 1.05

            # Sécurité : ne pas dépasser des valeurs extrêmes
            adjustment_factor = max(0.5, min(1.2, adjustment_factor))

        # Si on n'a pas atteint la tolérance, retourner la meilleure route trouvée
        if best_route:
            logger.warning(f"WARNING [Bearing {bearing}°] Distance cible non atteinte apres {max_iterations} iterations. "
                          f"Meilleur resultat: ecart de {best_distance_diff:.2f}km")
            return best_route

        return None

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
