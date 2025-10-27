"""
Script de démarrage pour Render.com
"""
import sys
import os

# Ajouter le répertoire backend au path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Changer le répertoire courant vers backend pour les imports
os.chdir(backend_path)

# Maintenant importer l'application
from main import app

# C'est tout ! Uvicorn utilisera cette variable
