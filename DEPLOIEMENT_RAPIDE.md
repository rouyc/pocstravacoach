# Déploiement Rapide sur Vercel

## ⚠️ Avertissement Important

**Problème de Timeout sur Vercel :** La génération de parcours peut prendre 10-20 secondes, mais Vercel a une limite de **10 secondes** pour les fonctions serverless gratuites.

**Recommandation :** Pour un POC fonctionnel en production, utilisez plutôt **Render** (gratuit, sans timeout).

---

## Option 1 : Déploiement Vercel (Rapide mais avec Limitations)

### Étapes Rapides

1. **Créer un repo GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   gh repo create strava-coach-poc --public --source=. --push
   ```

2. **Connecter à Vercel**
   - Allez sur [vercel.com](https://vercel.com)
   - Cliquez "Add New Project"
   - Importez votre repo GitHub
   - Cliquez "Deploy"

3. **Tester**
   - Ouvrez `https://VOTRE_PROJET.vercel.app/app`

### Problèmes Attendus
- ⚠️ Timeout après 10 secondes
- ⚠️ Génération peut échouer pour longues distances

---

## Option 2 : Render (Recommandé pour Production)

### Avantages Render
- ✅ Gratuit
- ✅ Pas de limite de timeout
- ✅ Parfait pour FastAPI
- ✅ Plus stable pour ce POC

### Déploiement sur Render

1. **Créer un compte sur [render.com](https://render.com)**

2. **Créer un Web Service**
   - New → Web Service
   - Connecter GitHub
   - Sélectionner votre repo

3. **Configuration**
   ```
   Name: strava-coach-poc
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Déployer**
   - Cliquez "Create Web Service"
   - Attendez 2-3 minutes

5. **Tester**
   - Votre app sera sur `https://strava-coach-poc.onrender.com/app`

---

## Option 3 : Architecture Hybride (Meilleur des Deux Mondes)

### Backend sur Render + Frontend sur Vercel

**Étape 1 : Déployer le Backend sur Render**
- Suivre les étapes de l'Option 2

**Étape 2 : Modifier le Frontend**
Éditer `frontend/app.js` ligne 2 :
```javascript
const API_BASE_URL = 'https://VOTRE_APP.onrender.com';
```

**Étape 3 : Déployer le Frontend sur Vercel**
- Créer un nouveau projet Vercel
- Importer uniquement le dossier `frontend/`

---

## Quelle Option Choisir ?

| Critère | Vercel | Render | Hybride |
|---------|--------|--------|---------|
| Rapidité déploiement | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Stabilité | ⚠️ Timeout | ✅ Stable | ✅ Stable |
| Gratuit | ✅ Oui | ✅ Oui | ✅ Oui |
| Recommandé POC | ❌ Non | ✅ Oui | ⭐⭐⭐ |

**Verdict : Pour ce POC, utilisez Render (Option 2) ou Hybride (Option 3)**

---

## Commandes Git Rapides

```bash
# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "POC Strava+Coach - Générateur de parcours"

# Créer repo GitHub (avec GitHub CLI)
gh repo create strava-coach-poc --public --source=. --push

# OU avec git classique
git remote add origin https://github.com/USERNAME/strava-coach-poc.git
git branch -M main
git push -u origin main
```

---

## Après le Déploiement

### Tester l'API
```bash
curl -X POST "https://VOTRE_URL/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Tour Eiffel, Paris",
    "distance_km": 5.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'
```

### Tester l'Interface
Ouvrez : `https://VOTRE_URL/app`

---

## Troubleshooting

### Erreur "No module named X"
- Vérifiez que `requirements.txt` est à jour
- Rebuild le projet

### Timeout sur Vercel
- Normal pour ce POC
- Migrez vers Render

### Erreur 500
- Vérifiez les logs
- Vérifiez que toutes les variables d'environnement sont définies

---

**Questions ? Consultez [DEPLOIEMENT_VERCEL.md](DEPLOIEMENT_VERCEL.md) pour le guide complet.**
