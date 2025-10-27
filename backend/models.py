from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class TrainingType(str, Enum):
    """Types d'entraînement supportés"""
    FRACTIONNE = "fractionne"
    ENDURANCE = "endurance"
    TEMPO = "tempo"
    RECUPERATION = "recuperation"


class ElevationPreference(str, Enum):
    """Préférences de dénivelé"""
    PLAT = "plat"
    VALLONNE = "vallonne"
    MONTAGNEUX = "montagneux"


class RouteRequest(BaseModel):
    """Requête de génération de parcours"""
    start_location: str = Field(..., description="Adresse ou coordonnées GPS du point de départ")
    distance_km: float = Field(..., gt=0, le=100, description="Distance cible en kilomètres (max 100km)")
    training_type: TrainingType = Field(default=TrainingType.ENDURANCE, description="Type d'entraînement")
    elevation_preference: ElevationPreference = Field(default=ElevationPreference.PLAT, description="Préférence de dénivelé")
    avoid_busy_roads: bool = Field(default=True, description="Éviter les routes passantes")
    prefer_parks: bool = Field(default=True, description="Privilégier les parcs et sentiers")

    class Config:
        json_schema_extra = {
            "example": {
                "start_location": "Place de la République, Paris",
                "distance_km": 10.0,
                "training_type": "endurance",
                "elevation_preference": "plat",
                "avoid_busy_roads": True,
                "prefer_parks": True
            }
        }


class Coordinates(BaseModel):
    """Coordonnées GPS"""
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class RouteMetrics(BaseModel):
    """Métriques du parcours"""
    distance_km: float = Field(..., description="Distance réelle du parcours")
    elevation_gain_m: float = Field(..., description="Dénivelé positif en mètres")
    elevation_loss_m: float = Field(..., description="Dénivelé négatif en mètres")
    estimated_duration_min: Optional[int] = Field(None, description="Durée estimée en minutes")


class RouteResponse(BaseModel):
    """Réponse contenant le parcours généré"""
    geojson: dict = Field(..., description="Parcours au format GeoJSON")
    gpx: str = Field(..., description="Parcours au format GPX")
    metrics: RouteMetrics = Field(..., description="Métriques du parcours")
    waypoints: List[Coordinates] = Field(..., description="Points de passage du parcours")
    start_address: str = Field(..., description="Adresse de départ résolue")


class ErrorResponse(BaseModel):
    """Réponse d'erreur"""
    error: str
    details: Optional[str] = None
