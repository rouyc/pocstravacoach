# Exemples de Tests - Générateur de Parcours

Ce document contient des exemples de requêtes pour tester le POC.

---

## Tests via l'Interface Web

### Accès
```
http://localhost:8000/app
```

### Test 1 : Parcours Court et Plat (Paris)
**Paramètres :**
- Point de départ : `Tour Eiffel, Paris`
- Distance : `5 km`
- Type : `Endurance`
- Dénivelé : `Plat`
- Éviter routes passantes : ✅
- Privilégier parcs : ✅

**Résultat attendu :**
- Distance : ~5 km (±0.5 km)
- Dénivelé positif : < 75m (15m/km × 5)
- Temps de génération : 10-15 secondes

---

### Test 2 : Parcours Moyen avec Dénivelé (Paris)
**Paramètres :**
- Point de départ : `Parc des Buttes-Chaumont, Paris`
- Distance : `10 km`
- Type : `Tempo`
- Dénivelé : `Vallonné`
- Éviter routes passantes : ✅
- Privilégier parcs : ✅

**Résultat attendu :**
- Distance : ~10 km (±1 km)
- Dénivelé positif : 150-400m (15-40m/km × 10)
- Zone naturellement vallonnée

---

### Test 3 : Longue Distance (Paris)
**Paramètres :**
- Point de départ : `Place de la République, Paris`
- Distance : `15 km`
- Type : `Endurance`
- Dénivelé : `Plat`
- Éviter routes passantes : ✅
- Privilégier parcs : ✅

**Résultat attendu :**
- Distance : ~15 km (±1.5 km)
- Parcours traversant plusieurs quartiers
- Temps de génération : 15-20 secondes

---

### Test 4 : Fractionné Court
**Paramètres :**
- Point de départ : `Jardin du Luxembourg, Paris`
- Distance : `3 km`
- Type : `Fractionné`
- Dénivelé : `Plat`
- Éviter routes passantes : ✅
- Privilégier parcs : ✅

**Résultat attendu :**
- Parcours idéal pour intervalles
- Zone parc privilégiée
- Distance précise pour séances structurées

---

## Tests via cURL (API)

### Test 1 : Requête Basique
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

**Vérifier dans la réponse :**
- `start_address` contient "Tour Eiffel"
- `metrics.distance_km` ≈ 5.0
- `geojson.features` n'est pas vide
- `gpx` commence par `<?xml`

---

### Test 2 : Différents Types d'Entraînement
```bash
# Fractionné
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Place de la République, Paris",
    "distance_km": 8.0,
    "training_type": "fractionne",
    "elevation_preference": "plat"
  }'

# Tempo
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Jardin du Luxembourg, Paris",
    "distance_km": 10.0,
    "training_type": "tempo",
    "elevation_preference": "vallonne"
  }'

# Récupération
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Champs-Élysées, Paris",
    "distance_km": 6.0,
    "training_type": "recuperation",
    "elevation_preference": "plat"
  }'
```

---

### Test 3 : Différentes Distances
```bash
# Courte (3km)
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Notre-Dame, Paris",
    "distance_km": 3.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'

# Moyenne (15km)
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Gare du Nord, Paris",
    "distance_km": 15.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'

# Longue (25km)
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Montparnasse, Paris",
    "distance_km": 25.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'
```

---

### Test 4 : Gestion d'Erreurs

#### Adresse invalide
```bash
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "XYZ123INVALID",
    "distance_km": 5.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'
```
**Résultat attendu :** Erreur 400 "Impossible de géocoder l'adresse"

#### Distance invalide
```bash
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Tour Eiffel, Paris",
    "distance_km": 150.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'
```
**Résultat attendu :** Erreur 422 (validation Pydantic)

#### Paramètre manquant
```bash
curl -X POST "http://localhost:8000/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Tour Eiffel, Paris"
  }'
```
**Résultat attendu :** Erreur 422 (champ requis manquant)

---

## Tests via Python (Requests)

### Installation
```bash
pip install requests
```

### Script de Test
```python
import requests
import json

# Configuration
API_URL = "http://localhost:8000/api/generate-route"

# Données de test
test_data = {
    "start_location": "Tour Eiffel, Paris",
    "distance_km": 10.0,
    "training_type": "endurance",
    "elevation_preference": "plat",
    "avoid_busy_roads": True,
    "prefer_parks": True
}

# Requête
print("Envoi de la requête...")
response = requests.post(API_URL, json=test_data)

# Vérification
if response.status_code == 200:
    data = response.json()
    print("✅ Succès!")
    print(f"Distance: {data['metrics']['distance_km']} km")
    print(f"D+ : {data['metrics']['elevation_gain_m']} m")
    print(f"D- : {data['metrics']['elevation_loss_m']} m")
    print(f"Adresse départ: {data['start_address']}")
    print(f"Nombre de waypoints: {len(data['waypoints'])}")

    # Sauvegarder le GPX
    with open("parcours_test.gpx", "w", encoding="utf-8") as f:
        f.write(data['gpx'])
    print("GPX sauvegardé : parcours_test.gpx")

else:
    print(f"❌ Erreur {response.status_code}")
    print(response.json())
```

---

## Tests de Charge (Optionnel)

### Avec Apache Bench
```bash
# Installer Apache Bench
# Ubuntu: sudo apt-get install apache2-utils
# Mac: brew install httpd

# Test simple (10 requêtes séquentielles)
ab -n 10 -c 1 -p test_payload.json \
   -T "application/json" \
   http://localhost:8000/api/generate-route
```

**Fichier test_payload.json :**
```json
{
  "start_location": "Tour Eiffel, Paris",
  "distance_km": 5.0,
  "training_type": "endurance",
  "elevation_preference": "plat"
}
```

**⚠️ Attention :** Nominatim a une limite de 1 req/sec, donc les tests de charge échoueront !

---

## Vérification de la Qualité du GPX

### Méthode 1 : Visualisation en ligne
1. Aller sur https://www.gpsvisualizer.com/
2. Cliquer sur "Draw a map"
3. Uploader le fichier GPX téléchargé
4. Vérifier que le tracé s'affiche correctement

### Méthode 2 : Import dans Strava
1. Créer une activité manuelle sur Strava
2. Importer le fichier GPX
3. Vérifier le tracé et les métriques

### Méthode 3 : Validation XML
```bash
# Installer xmllint (inclus dans libxml2)
# Ubuntu: sudo apt-get install libxml2-utils

# Valider le GPX
xmllint --noout parcours_test.gpx
```

---

## Checklist de Tests Complets

### Fonctionnels
- [ ] Génération de parcours réussie (5km, 10km, 15km)
- [ ] Adresse géocodée correctement
- [ ] Distance générée proche de la cible (±10%)
- [ ] Dénivelé conforme à la préférence
- [ ] GPX valide et importable
- [ ] Carte affichée correctement
- [ ] Export GPX fonctionnel

### Non-fonctionnels
- [ ] Temps de réponse < 20 secondes
- [ ] Gestion d'erreurs gracieuse
- [ ] Messages d'erreur clairs
- [ ] Documentation API accessible
- [ ] Interface responsive (mobile/desktop)

### Edge Cases
- [ ] Adresse invalide → erreur explicite
- [ ] Distance trop grande (>100km) → rejetée
- [ ] Distance trop petite (<1km) → rejetée
- [ ] Caractères spéciaux dans l'adresse
- [ ] Coordonnées GPS directes (lat,lon)

---

## Bugs Connus / Limitations

### 1. Parcours Aller-Retour
**Problème :** Le parcours fait un aller-retour sur le même chemin
**Workaround :** Accepté pour le POC, amélioration prévue en V2

### 2. Temps de Génération
**Problème :** Peut prendre 15-20 secondes sur longues distances
**Cause :** Rate limit Nominatim + multiples appels OSRM
**Workaround :** Message de patience dans l'UI

### 3. Précision Dénivelé
**Problème :** Dénivelé parfois imprécis (±20m)
**Cause :** Résolution limitée des données SRTM
**Workaround :** Considérer comme estimation

### 4. Zones Rurales
**Problème :** Moins bon résultat en zones peu denses
**Cause :** Moins de chemins alternatifs dans OSM
**Workaround :** Privilégier les zones urbaines pour le POC

---

## Ressources Utiles

### Endpoints de Test
- Health check : http://localhost:8000/health
- API docs : http://localhost:8000/docs
- OpenAPI JSON : http://localhost:8000/openapi.json

### Outils Externes
- Nominatim Test : https://nominatim.openstreetmap.org/
- OSRM Demo : https://map.project-osrm.org/
- GPX Validator : https://www.gpsvisualizer.com/

---

**Bon testing! 🚀**
