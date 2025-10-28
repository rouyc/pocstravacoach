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


class RouteType(str, Enum):
    """Type de parcours"""
    LOOP = "loop"  # Boucle
    OUT_AND_BACK = "out_and_back"  # Aller-retour
    BOTH = "both"  # Proposer les deux options


class SurfacePreferences(BaseModel):
    """Préférences de type de surface"""
    # Types de routes
    highway: bool = Field(default=False, description="Route principale/autoroute")
    primary: bool = Field(default=True, description="Route primaire")
    secondary: bool = Field(default=True, description="Route secondaire")
    residential: bool = Field(default=True, description="Rue résidentielle")

    # Chemins et pistes
    cycleway: bool = Field(default=True, description="Piste cyclable")
    footway: bool = Field(default=True, description="Chemin piéton")
    path: bool = Field(default=True, description="Sentier")
    track: bool = Field(default=True, description="Chemin carrossable")

    # Sentiers naturels
    trail: bool = Field(default=False, description="Sentier de randonnée")
    bridleway: bool = Field(default=False, description="Chemin équestre")


class SurfaceTypes(BaseModel):
    """Types de revêtement de surface"""
    paved: bool = Field(default=True, description="Goudron/béton")
    gravel: bool = Field(default=False, description="Gravier")
    dirt: bool = Field(default=False, description="Terre")
    grass: bool = Field(default=False, description="Herbe")


class RouteRequest(BaseModel):
    """Requête de génération de parcours"""
    start_location: str = Field(..., description="Adresse ou coordonnées GPS du point de départ")
    distance_km: float = Field(..., gt=0, le=100, description="Distance cible en kilomètres (max 100km)")
    training_type: TrainingType = Field(default=TrainingType.ENDURANCE, description="Type d'entraînement")
    elevation_preference: ElevationPreference = Field(default=ElevationPreference.PLAT, description="Préférence de dénivelé")

    # Options de base (rétrocompatibilité)
    avoid_busy_roads: bool = Field(default=True, description="Éviter les routes passantes")
    prefer_parks: bool = Field(default=True, description="Privilégier les parcs et sentiers")

    # Nouvelles options avancées
    route_type: RouteType = Field(default=RouteType.OUT_AND_BACK, description="Type de parcours (boucle ou aller-retour)")
    surface_preferences: Optional[SurfacePreferences] = Field(default=None, description="Préférences détaillées de type de route")
    surface_types: Optional[SurfaceTypes] = Field(default=None, description="Préférences de revêtement de surface")

    class Config:
        json_schema_extra = {
            "example": {
                "start_location": "Place de la République, Paris",
                "distance_km": 10.0,
                "training_type": "endurance",
                "elevation_preference": "plat",
                "avoid_busy_roads": True,
                "prefer_parks": True,
                "route_type": "loop",
                "surface_preferences": {
                    "highway": False,
                    "primary": True,
                    "secondary": True,
                    "residential": True,
                    "cycleway": True,
                    "footway": True,
                    "path": True,
                    "track": True,
                    "trail": False,
                    "bridleway": False
                },
                "surface_types": {
                    "paved": True,
                    "gravel": False,
                    "dirt": False,
                    "grass": False
                }
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
