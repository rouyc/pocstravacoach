# 🏗️ Stack Technique Retenue

## Backend : Python + FastAPI

- **FastAPI** : performances excellentes, documentation auto-générée, typage moderne
- **Asyncio** pour les appels API externes non-bloquants
- **Pydantic** pour la validation des données

## API Cartographique : OpenStreetMap + Overpass API + OSRM

- Gratuit et open-source
- **Overpass API** : extraction de données OSM (parcs, routes, dénivelé)
- **OSRM** (Open Source Routing Machine) : calcul d'itinéraires optimisés
- **Alternative** : GraphHopper (plus flexible mais plus complexe)

## Frontend : HTML/JS + Leaflet

- **Leaflet** : léger, excellent pour OSM, gratuit
- **Vanilla JS** pour le POC (pas de framework lourd)
- **Bootstrap** pour l'UI rapide

## Données géospatiales

- **GeoJSON** pour l'échange de données
- **GPX** pour l'export

## 📐 Architecture du Système

```text
┌─────────────────────────────────────────┐
│         Frontend (HTML/JS)              │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Form Input   │  │  Leaflet Map    │ │
│  │ (Training    │  │  (Route         │ │
│  │  params)     │  │   Display)      │ │
│  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
              │ HTTP REST API
              ▼
┌─────────────────────────────────────────┐
│      Backend (FastAPI)                  │
│  ┌─────────────────────────────────┐   │
│  │  Route Generator Service        │   │
│  │  ┌──────────────────────────┐   │   │
│  │  │ 1. Geocoding             │   │   │
│  │  │ 2. Area Analysis         │   │   │
│  │  │ 3. Route Generation      │   │   │
│  │  │ 4. Distance Optimization │   │   │
│  │  │ 5. Elevation Calculation │   │   │
│  │  └──────────────────────────┘   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│      External APIs                      │
│  ┌───────────┐  ┌──────────────────┐   │
│  │ Nominatim │  │ OSRM / Overpass  │   │
│  │ (Geocode) │  │ (Routing/Data)   │   │
│  └───────────┘  └──────────────────┘   │
└─────────────────────────────────────────┘
```

## 🔧 Algorithme de Génération de Parcours

### Approche en 5 étapes

#### 1. Géocodage

Convertir l'adresse de départ en coordonnées GPS (Nominatim)

#### 2. Analyse de zone

Extraire les points d'intérêt dans un rayon adapté :

- Routes/chemins selon préférences (éviter grandes routes)
- Parcs, sentiers
- Données d'élévation

#### 3. Génération de parcours candidats

- **Approche "aller-retour"** : simple (facile à implémenter)
- **Approche "boucle"** : plus complexe, meilleure UX
- Utiliser OSRM pour calculer des routes vers des points intermédiaires

#### 4. Optimisation distance

- Ajuster les points intermédiaires pour atteindre la distance cible
- Algorithme itératif : si distance < cible, chercher point plus éloigné

#### 5. Calcul dénivelé

- Utiliser Open-Elevation API ou SRTM data
- Filtrer selon préférence (plat/vallonné/montagneux)

## 📁 Structure du Projet

```text
strava-coach-poc/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── models.py               # Pydantic models
│   ├── services/
│   │   ├── geocoding.py
│   │   ├── route_generator.py
│   │   └── elevation.py
│   ├── utils/
│   │   └── geo_helpers.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md
```

## 🎯 Endpoint API Principal

### POST /api/generate-route

**Request:**

```json
{
  "start_location": "15 rue de Rivoli, Paris",
  "distance_km": 10,
  "training_type": "endurance",
  "elevation_preference": "plat",
  "avoid_busy_roads": true,
  "prefer_parks": true
}
```

**Response:**

```json
{
  "route": {
    "geojson": {...},
    "gpx": "...",
    "metrics": {
      "distance_km": 10.02,
      "elevation_gain_m": 45,
      "elevation_loss_m": 45
    },
    "waypoints": [...]
  }
}
```

## ⚠️ Limitations du POC

- **Pas d'optimisation avancée** : algorithme simple, pas de machine learning
- **API publiques** : rate limits (Nominatim : 1 req/sec)
- **Dénivelé approximatif** : précision limitée selon les données
- **Pas de cache** : chaque requête recalcule tout
