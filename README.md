# Strava+Coach - POC Générateur de Parcours

## Description

POC d'un générateur de parcours d'entraînement intelligent pour l'application Strava+Coach. Ce prototype permet de générer automatiquement des parcours de course à pied personnalisés en fonction des paramètres d'entraînement.

## Fonctionnalités

- **Génération de parcours personnalisés** basée sur :
  - Distance cible (1-100 km)
  - Type d'entraînement (endurance, fractionné, tempo, récupération)
  - Préférence de dénivelé (plat, vallonné, montagneux)
  - Point de départ (adresse ou coordonnées GPS)
  - Préférences utilisateur (éviter routes passantes, privilégier parcs)

- **Visualisation interactive** :
  - Carte Leaflet avec affichage du tracé
  - Métriques détaillées du parcours
  - Point de départ marqué

- **Export** :
  - Format GPX pour import dans montres/applications GPS

## Architecture Technique

### Stack

- **Backend** : Python 3.8+ avec FastAPI
- **Frontend** : HTML/CSS/JavaScript avec Leaflet
- **APIs externes** :
  - Nominatim (OpenStreetMap) pour le géocodage
  - OSRM pour le calcul d'itinéraires
  - Open-Elevation pour les données d'altitude

### Structure du Projet

```
strava-coach-poc/
├── backend/
│   ├── main.py                 # Application FastAPI principale
│   ├── models.py               # Modèles Pydantic
│   ├── services/
│   │   ├── geocoding.py        # Service de géocodage
│   │   ├── route_generator.py  # Générateur de parcours
│   │   └── elevation.py        # Calcul d'élévation
│   ├── utils/
│   │   └── geo_helpers.py      # Fonctions géospatiales
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Interface utilisateur
│   ├── style.css               # Styles
│   └── app.js                  # Logique frontend
└── README.md
```

## Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le projet** (ou naviguer vers le dossier)

   ```bash
   cd testmap
   ```

2. **Installer les dépendances Python**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Démarrer le serveur backend**

   ```bash
   python main.py
   ```

   Le serveur démarre sur `http://localhost:8000`

4. **Accéder à l'application**
   - Interface web : `http://localhost:8000/app`
   - Documentation API : `http://localhost:8000/docs`

## Utilisation

### Via l'interface web

1. Ouvrir `http://localhost:8000/app` dans votre navigateur
2. Remplir le formulaire :
   - Point de départ (ex: "Place de la République, Paris")
   - Distance souhaitée
   - Type d'entraînement
   - Préférence de dénivelé
   - Options additionnelles
3. Cliquer sur "Générer le parcours"
4. Visualiser le parcours sur la carte
5. Exporter en GPX si besoin

### Via l'API REST

**Endpoint** : `POST /api/generate-route`

**Exemple de requête** :

```bash
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Place de la République, Paris",
    "distance_km": 10.0,
    "training_type": "endurance",
    "elevation_preference": "plat",
    "avoid_busy_roads": true,
    "prefer_parks": true
  }'
```

**Exemple de réponse** :

```json
{
  "geojson": { ... },
  "gpx": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
  "metrics": {
    "distance_km": 10.02,
    "elevation_gain_m": 45.2,
    "elevation_loss_m": 45.1,
    "estimated_duration_min": 50
  },
  "waypoints": [...],
  "start_address": "Place de la République, Paris, Île-de-France, France"
}
```

## Algorithme de Génération

Le générateur utilise une approche en plusieurs étapes :

1. **Géocodage** : Conversion de l'adresse en coordonnées GPS (Nominatim)

2. **Génération de candidats** :
   - Exploration de 8 directions différentes (tous les 45°)
   - Calcul d'un parcours aller-retour pour chaque direction
   - Utilisation d'OSRM pour le routing

3. **Scoring et sélection** :
   - Évaluation de chaque parcours candidat
   - Pénalités pour écart de distance et dénivelé non conforme
   - Sélection du meilleur parcours

4. **Enrichissement** :
   - Calcul des élévations (Open-Elevation)
   - Calcul des métriques (distance, dénivelé, durée)
   - Génération du GPX

## Limitations du POC

- **Rate limits** : Les APIs publiques ont des limitations (Nominatim: 1 req/sec)
- **Algorithme simple** : Approche aller-retour, pas d'optimisation avancée pour les boucles
- **Pas de cache** : Chaque requête recalcule tout
- **Précision d'élévation** : Dépend de la qualité des données SRTM
- **Pas de prise en compte du trafic** : Les préférences de routes sont simplifiées

## Évolutions Futures

### Court terme

- [ ] Amélioration de l'algorithme de boucle (éviter aller-retour)
- [ ] Cache Redis pour les requêtes fréquentes
- [ ] Gestion des erreurs plus robuste
- [ ] Tests unitaires et d'intégration

### Moyen terme

- [ ] Intégration de données temps réel (météo, trafic)
- [ ] Personnalisation basée sur l'historique utilisateur
- [ ] Support du vélo et autres activités
- [ ] API de sauvegarde/partage de parcours

### Long terme

- [ ] Machine Learning pour optimisation basée sur les préférences
- [ ] Génération de parcours multi-critères (zones d'entraînement)
- [ ] Intégration nutrition et hydratation
- [ ] Application mobile native

## Technologies Utilisées

### Backend

- **FastAPI** : Framework web moderne et performant
- **Pydantic** : Validation des données
- **httpx** : Client HTTP asynchrone
- **gpxpy** : Génération de fichiers GPX
- **geopy** : Utilitaires géospatiaux

### Frontend

- **Leaflet** : Bibliothèque de cartographie interactive
- **Bootstrap 5** : Framework CSS
- **Vanilla JavaScript** : Pas de framework lourd pour le POC

### APIs Externes

- **Nominatim** : Géocodage OpenStreetMap (gratuit)
- **OSRM** : Routing (gratuit)
- **Open-Elevation** : Données d'altitude (gratuit)

## Contribution

Ce POC est un prototype de démonstration. Pour contribuer :

1. Identifier les bugs ou améliorations
2. Tester avec différentes localisations
3. Proposer des optimisations d'algorithme

## Licence

POC à usage éducatif et de démonstration.

## Contact

Pour toute question sur ce POC, consulter la documentation FastAPI générée automatiquement : `http://localhost:8000/docs`
