import httpx
from typing import Optional, Tuple
import time


class GeocodingService:
    """Service de géocodage utilisant Nominatim (OpenStreetMap)"""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            "User-Agent": "StravaCoachPOC/1.0"
        }
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Respecter la limite de 1 req/sec de Nominatim

    async def geocode(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        Convertit une adresse en coordonnées GPS

        Args:
            address: Adresse à géocoder

        Returns:
            Tuple (latitude, longitude, adresse_formatée) ou None si échec
        """
        # Respecter le rate limit
        await self._wait_for_rate_limit()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        "q": address,
                        "format": "json",
                        "limit": 1
                    },
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                if not data:
                    return None

                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                display_name = result["display_name"]

                return lat, lon, display_name

            except Exception as e:
                print(f"Erreur de géocodage: {e}")
                return None

    async def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convertit des coordonnées GPS en adresse

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            Adresse formatée ou None si échec
        """
        # Respecter le rate limit
        await self._wait_for_rate_limit()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/reverse",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "format": "json"
                    },
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                return data.get("display_name")

            except Exception as e:
                print(f"Erreur de géocodage inverse: {e}")
                return None

    async def _wait_for_rate_limit(self):
        """Attend pour respecter le rate limit de Nominatim"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            time.sleep(wait_time)

        self.last_request_time = time.time()
