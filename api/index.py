"""
Point d'entrée pour Vercel serverless
"""
import sys
import os

# Ajouter le répertoire backend au path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from backend.main import app

# Vercel handler
handler = app
