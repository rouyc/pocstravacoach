# Guide de Démarrage - Strava+Coach POC

## Installation et Démarrage Rapide

### 1. Vérifier que Python est installé
```bash
python --version
```
Version requise : Python 3.8 ou supérieur

### 2. Installer les dépendances
```bash
cd backend
pip install -r requirements.txt
```

### 3. Démarrer le serveur
Depuis le répertoire racine du projet :
```bash
python start_server.py
```

Vous devriez voir :
```
============================================================
Strava+Coach - Route Generator API
============================================================

Server starting...
  - API docs: http://localhost:8000/docs
  - Web app: http://localhost:8000/app

Press CTRL+C to stop
============================================================
```

### 4. Accéder à l'application

#### Interface Web
Ouvrez votre navigateur et accédez à :
```
http://localhost:8000/app
```

#### Documentation API (Swagger)
Pour explorer l'API interactivement :
```
http://localhost:8000/docs
```

## Utilisation de l'Application Web

### Étape 1 : Remplir le formulaire
1. **Point de départ** : Entrez une adresse (ex: "Tour Eiffel, Paris")
2. **Distance** : Choisissez la distance souhaitée en km (1-100)
3. **Type d'entraînement** : Sélectionnez parmi :
   - Endurance (course longue et lente)
   - Fractionné (intervalles rapides)
   - Tempo (allure soutenue)
   - Récupération (course facile)
4. **Dénivelé** : Choisissez :
   - Plat (< 15m D+/km)
   - Vallonné (15-40m D+/km)
   - Montagneux (> 40m D+/km)
5. **Préférences** : Cochez les options souhaitées

### Étape 2 : Générer le parcours
- Cliquez sur "Générer le parcours"
- Patientez quelques secondes (l'API contacte plusieurs services externes)
- Le parcours s'affiche sur la carte

### Étape 3 : Consulter les métriques
Les métriques calculées apparaissent dans le panneau latéral :
- Distance réelle du parcours
- Dénivelé positif
- Dénivelé négatif
- Durée estimée

### Étape 4 : Exporter (optionnel)
- Cliquez sur "Exporter GPX" pour télécharger le fichier
- Importez-le dans votre montre GPS ou application de running

## Test de l'API via cURL

### Exemple de requête
```bash
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Tour Eiffel, Paris",
    "distance_km": 5.0,
    "training_type": "endurance",
    "elevation_preference": "plat",
    "avoid_busy_roads": true,
    "prefer_parks": true
  }'
```

### Exemple de réponse
```json
{
  "geojson": {
    "type": "FeatureCollection",
    "features": [...]
  },
  "gpx": "<?xml version=\"1.0\"?>...",
  "metrics": {
    "distance_km": 5.02,
    "elevation_gain_m": 12.5,
    "elevation_loss_m": 12.3,
    "estimated_duration_min": 25
  },
  "waypoints": [...],
  "start_address": "Tour Eiffel, Avenue Anatole France, Paris..."
}
```

## Exemples de Parcours à Tester

### Paris
- **Courte distance (5km)** : "Jardin du Luxembourg, Paris"
- **Distance moyenne (10km)** : "Place de la République, Paris"
- **Longue distance (15km)** : "Parc des Buttes-Chaumont, Paris"

### Autres villes (si vous testez ailleurs)
- **Lyon** : "Place Bellecour, Lyon"
- **Marseille** : "Vieux-Port, Marseille"
- **Toulouse** : "Place du Capitole, Toulouse"

## Résolution de Problèmes

### Le serveur ne démarre pas
- Vérifiez que le port 8000 n'est pas déjà utilisé
- Vérifiez que toutes les dépendances sont installées

### "Impossible de géocoder l'adresse"
- Vérifiez que l'adresse est correcte et reconnue
- Essayez avec une adresse plus précise
- Vérifiez votre connexion internet

### Le parcours met du temps à générer
- C'est normal ! L'API contacte plusieurs services externes :
  - Nominatim pour le géocodage (1 req/sec limit)
  - OSRM pour le routing
  - Open-Elevation pour les données d'altitude
- Temps moyen : 10-15 secondes

### La carte ne s'affiche pas
- Vérifiez que vous accédez à l'URL correcte : `http://localhost:8000/app`
- Vérifiez votre connexion internet (Leaflet charge des tuiles depuis OpenStreetMap)
- Vérifiez la console du navigateur pour les erreurs

## Architecture des Fichiers

```
testmap/
├── backend/
│   ├── main.py              # API FastAPI principale
│   ├── models.py            # Modèles de données
│   ├── services/
│   │   ├── geocoding.py     # Géocodage Nominatim
│   │   ├── elevation.py     # Calcul d'élévation
│   │   └── route_generator.py  # Génération de parcours
│   └── utils/
│       └── geo_helpers.py   # Fonctions géospatiales
├── frontend/
│   ├── index.html           # Interface utilisateur
│   ├── style.css            # Styles
│   └── app.js               # Logique JavaScript
├── start_server.py          # Script de démarrage
└── README.md                # Documentation complète
```

## Fonctionnement Technique

### 1. Géocodage (services/geocoding.py)
- Convertit l'adresse en coordonnées GPS
- Utilise Nominatim (OpenStreetMap)
- Respecte la limite de 1 requête/seconde

### 2. Génération de Parcours (services/route_generator.py)
**Algorithme :**
1. Teste 8 directions différentes (tous les 45°)
2. Pour chaque direction :
   - Calcule un point de destination à distance/2
   - Utilise OSRM pour générer l'aller
   - Crée le retour en inversant le chemin
3. Évalue chaque parcours candidat (score)
4. Sélectionne le meilleur parcours

**Critères de scoring :**
- Écart par rapport à la distance cible
- Conformité au dénivelé souhaité

### 3. Calcul d'Élévation (services/elevation.py)
- Récupère les altitudes via Open-Elevation API
- Calcule le dénivelé positif et négatif
- Interpole les valeurs si besoin

### 4. Export GPX
- Génère un fichier GPX standard
- Compatible avec Garmin, Suunto, Polar, etc.
- Contient les métadonnées du parcours

## Limitations Actuelles

1. **Approche aller-retour** : Le parcours fait un aller-retour, pas une boucle fermée
2. **Pas de cache** : Chaque requête recalcule tout
3. **APIs publiques gratuites** : Soumises à des rate limits
4. **Algorithme simple** : Pas d'optimisation avancée

## Prochaines Évolutions Possibles

- Génération de boucles fermées (pas d'aller-retour)
- Prise en compte des zones d'entraînement (FC, allure)
- Support du vélo et autres sports
- Sauvegarde et partage de parcours
- Intégration météo temps réel
- Cache Redis pour performances

## Support

Pour toute question :
- Consultez le [README.md](README.md) pour la documentation complète
- Explorez l'API interactive : http://localhost:8000/docs
- Vérifiez les logs du serveur pour les erreurs

---

**Version** : 1.0.0 (POC)
**Dernière mise à jour** : Octobre 2025
