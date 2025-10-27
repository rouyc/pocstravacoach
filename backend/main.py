from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from models import RouteRequest, RouteResponse, ErrorResponse, Coordinates, RouteMetrics
from services.geocoding import GeocodingService
from services.elevation import ElevationService
from services.route_generator import RouteGenerator

# Initialisation de l'application
app = FastAPI(
    title="Strava+Coach Route Generator API",
    description="API de génération de parcours d'entraînement personnalisés",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des services
geocoding_service = GeocodingService()
elevation_service = ElevationService()
route_generator = RouteGenerator(elevation_service)


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Strava+Coach Route Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}


@app.post(
    "/api/generate-route",
    response_model=RouteResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def generate_route(request: RouteRequest):
    """
    Génère un parcours d'entraînement personnalisé

    Args:
        request: Paramètres du parcours à générer

    Returns:
        RouteResponse contenant le parcours généré avec toutes ses métriques

    Raises:
        HTTPException: Si le géocodage échoue ou si la génération échoue
    """
    try:
        # 1. Géocoder l'adresse de départ
        geocode_result = await geocoding_service.geocode(request.start_location)

        if not geocode_result:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de géocoder l'adresse: {request.start_location}"
            )

        start_lat, start_lon, resolved_address = geocode_result

        # 2. Générer le parcours
        coordinates, metrics, gpx = await route_generator.generate_route(
            start_lat, start_lon, request
        )

        if not coordinates:
            raise HTTPException(
                status_code=500,
                detail="Impossible de générer un parcours avec les paramètres fournis"
            )

        # 3. Créer le GeoJSON
        from utils.geo_helpers import coordinates_to_geojson
        geojson = coordinates_to_geojson(coordinates)

        # 4. Créer la liste des waypoints
        waypoints = [
            Coordinates(lat=lat, lon=lon)
            for lat, lon in coordinates
        ]

        # 5. Construire la réponse
        response = RouteResponse(
            geojson=geojson,
            gpx=gpx,
            metrics=RouteMetrics(**metrics),
            waypoints=waypoints,
            start_address=resolved_address
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération du parcours: {str(e)}"
        )


# Servir le frontend (désactivé en production Vercel)
# Vercel sert les fichiers statiques directement
if not os.getenv("VERCEL"):
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
    if os.path.exists(frontend_path):
        app.mount("/static", StaticFiles(directory=frontend_path), name="static")

        @app.get("/app")
        async def serve_frontend():
            """Sert l'application frontend"""
            index_path = os.path.join(frontend_path, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
            return {"error": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
