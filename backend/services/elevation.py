import httpx
from typing import List, Tuple


class ElevationService:
    """Service de calcul d'élévation utilisant Open-Elevation API"""

    def __init__(self):
        self.base_url = "https://api.open-elevation.com/api/v1/lookup"

    async def get_elevations(self, coordinates: List[Tuple[float, float]]) -> List[float]:
        """
        Récupère les élévations pour une liste de coordonnées

        Args:
            coordinates: Liste de tuples (lat, lon)

        Returns:
            Liste des élévations en mètres
        """
        if not coordinates:
            return []

        # Limiter le nombre de points pour éviter les timeouts
        # Open-Elevation peut gérer jusqu'à 1024 points
        max_points = 100
        if len(coordinates) > max_points:
            # Échantillonner les coordonnées
            step = len(coordinates) // max_points
            sampled_coords = coordinates[::step]
        else:
            sampled_coords = coordinates

        locations = [{"latitude": lat, "longitude": lon} for lat, lon in sampled_coords]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    json={"locations": locations},
                    timeout=30.0
                )
                response.raise_for_status()

                data = response.json()
                elevations = [result["elevation"] for result in data["results"]]

                # Si on a échantillonné, interpoler les valeurs manquantes
                if len(coordinates) > max_points:
                    elevations = self._interpolate_elevations(elevations, len(coordinates))

                return elevations

            except Exception as e:
                print(f"Erreur lors de la récupération des élévations: {e}")
                # Retourner des élévations nulles en cas d'erreur
                return [0.0] * len(coordinates)

    def _interpolate_elevations(self, elevations: List[float], target_length: int) -> List[float]:
        """
        Interpole linéairement les élévations pour atteindre la longueur cible

        Args:
            elevations: Liste d'élévations échantillonnées
            target_length: Longueur cible

        Returns:
            Liste d'élévations interpolées
        """
        if not elevations or target_length <= len(elevations):
            return elevations

        result = []
        step = (len(elevations) - 1) / (target_length - 1)

        for i in range(target_length):
            pos = i * step
            idx = int(pos)
            frac = pos - idx

            if idx >= len(elevations) - 1:
                result.append(elevations[-1])
            else:
                # Interpolation linéaire
                value = elevations[idx] * (1 - frac) + elevations[idx + 1] * frac
                result.append(value)

        return result

    def calculate_elevation_metrics(self, elevations: List[float]) -> Tuple[float, float]:
        """
        Calcule le dénivelé positif et négatif

        Args:
            elevations: Liste des élévations en mètres

        Returns:
            Tuple (dénivelé_positif, dénivelé_négatif)
        """
        if len(elevations) < 2:
            return 0.0, 0.0

        elevation_gain = 0.0
        elevation_loss = 0.0

        for i in range(len(elevations) - 1):
            diff = elevations[i + 1] - elevations[i]
            if diff > 0:
                elevation_gain += diff
            else:
                elevation_loss += abs(diff)

        return elevation_gain, elevation_loss

    def matches_elevation_preference(
        self,
        elevation_gain: float,
        distance_km: float,
        preference: str
    ) -> bool:
        """
        Vérifie si le dénivelé correspond à la préférence

        Args:
            elevation_gain: Dénivelé positif en mètres
            distance_km: Distance en kilomètres
            preference: "plat", "vallonne", ou "montagneux"

        Returns:
            True si correspond à la préférence
        """
        # Calculer le ratio dénivelé/distance (m/km)
        ratio = elevation_gain / distance_km if distance_km > 0 else 0

        if preference == "plat":
            return ratio < 15  # Moins de 15m de D+ par km
        elif preference == "vallonne":
            return 15 <= ratio < 40  # Entre 15 et 40m de D+ par km
        elif preference == "montagneux":
            return ratio >= 40  # Plus de 40m de D+ par km

        return True
