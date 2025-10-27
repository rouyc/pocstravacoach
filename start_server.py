"""
Script de démarrage du serveur Strava+Coach
"""
import sys
import os

# Ajouter le répertoire backend au Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    import uvicorn
    from backend.main import app

    print("=" * 60)
    print("Strava+Coach - Route Generator API")
    print("=" * 60)
    print("")
    print("Server starting...")
    print("  - API docs: http://localhost:8000/docs")
    print("  - Web app: http://localhost:8000/app")
    print("")
    print("Press CTRL+C to stop")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
