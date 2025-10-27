# Guide de Déploiement sur Vercel

## Prérequis

1. **Compte Vercel** : Créez un compte gratuit sur [vercel.com](https://vercel.com)
2. **Git** : Le projet doit être dans un repository Git (GitHub, GitLab, ou Bitbucket)
3. **Vercel CLI** (optionnel) : Pour déployer en ligne de commande

## Méthode 1 : Déploiement via l'Interface Web Vercel (Recommandé)

### Étape 1 : Préparer le Repository Git

```bash
# Initialiser Git (si pas déjà fait)
git init

# Ajouter tous les fichiers
git add .

# Créer le commit initial
git commit -m "Initial commit - Strava+Coach POC"

# Créer un repo sur GitHub et le lier
# (Suivre les instructions de GitHub)
git remote add origin https://github.com/VOTRE_USERNAME/strava-coach-poc.git
git branch -M main
git push -u origin main
```

### Étape 2 : Importer le Projet dans Vercel

1. Allez sur [vercel.com](https://vercel.com)
2. Cliquez sur **"Add New Project"**
3. Sélectionnez **"Import Git Repository"**
4. Choisissez votre repository GitHub
5. Cliquez sur **"Import"**

### Étape 3 : Configurer le Projet

Vercel devrait détecter automatiquement la configuration grâce au fichier `vercel.json`.

**Si demandé, configurez :**
- **Framework Preset** : Other
- **Build Command** : (laisser vide)
- **Output Directory** : (laisser vide)
- **Install Command** : `pip install -r requirements.txt`

### Étape 4 : Variables d'Environnement (Optionnel)

Si vous avez des clés API à ajouter plus tard :
1. Allez dans **Settings** → **Environment Variables**
2. Ajoutez vos variables

### Étape 5 : Déployer

1. Cliquez sur **"Deploy"**
2. Attendez 2-3 minutes
3. Votre application sera accessible sur `https://VOTRE_PROJET.vercel.app`

---

## Méthode 2 : Déploiement via Vercel CLI

### Installation de Vercel CLI

```bash
npm install -g vercel
```

### Connexion à Vercel

```bash
vercel login
```

### Déploiement

```bash
# Depuis le répertoire du projet
vercel

# Suivre les instructions :
# - Set up and deploy "~/testmap"? [Y/n] Y
# - Which scope? (sélectionner votre compte)
# - Link to existing project? [y/N] N
# - What's your project's name? strava-coach-poc
# - In which directory is your code located? ./
```

### Déploiement en Production

```bash
vercel --prod
```

---

## Structure des Fichiers pour Vercel

Voici les fichiers créés/modifiés pour le déploiement :

### 1. `vercel.json` (Configuration principale)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/main.py"
    },
    {
      "src": "/static/(.*)",
      "dest": "frontend/$1"
    },
    {
      "src": "/app",
      "dest": "frontend/index.html"
    },
    {
      "src": "/(.*)",
      "dest": "backend/main.py"
    }
  ]
}
```

### 2. `api/index.py` (Point d'entrée Vercel)
Point d'entrée pour les fonctions serverless Python de Vercel.

### 3. `requirements.txt` (Racine du projet)
Dépendances Python pour Vercel.

---

## Après le Déploiement

### Accéder à votre Application

Une fois déployé, Vercel vous donnera une URL :
```
https://strava-coach-poc.vercel.app
```

### Tester l'API

```bash
curl -X POST "https://strava-coach-poc.vercel.app/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Tour Eiffel, Paris",
    "distance_km": 10.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'
```

### Interface Web

Accédez à l'interface web :
```
https://strava-coach-poc.vercel.app/app
```

---

## Limitations de Vercel (Version Gratuite)

### Limites de la Fonction Serverless
- **Temps d'exécution maximum** : 10 secondes
- **Mémoire** : 1024 MB
- **Timeout** : 10s

⚠️ **Problème potentiel** : La génération de parcours peut prendre 10-20 secondes (appels à Nominatim, OSRM, Open-Elevation).

### Solutions aux Timeouts

**Option A : Optimiser les Requêtes**
- Utiliser un cache pour les géocodages fréquents
- Paralléliser les appels API

**Option B : Déployer sur une Plateforme sans Limite de Temps**
Alternatives recommandées :
- **Render** : Gratuit, pas de limite de timeout
- **Railway** : Gratuit, meilleur pour FastAPI
- **Fly.io** : Gratuit, très performant

---

## Déploiement Alternatif (Recommandé pour Production)

### Architecture Hybride

**Backend** → **Render** (gratuit, pas de timeout)
**Frontend** → **Vercel** (gratuit, CDN rapide)

### Étapes

1. **Déployer le backend sur Render** :
   - Créer un compte sur [render.com](https://render.com)
   - Créer un "Web Service"
   - Connecter votre repo GitHub
   - Build Command : `pip install -r backend/requirements.txt`
   - Start Command : `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

2. **Déployer le frontend sur Vercel** :
   - Déployer uniquement le dossier `frontend/`
   - Mettre à jour l'URL de l'API dans `frontend/app.js` :
   ```javascript
   const API_BASE_URL = 'https://VOTRE_APP.onrender.com';
   ```

---

## Monitoring et Logs

### Voir les Logs sur Vercel

1. Allez sur [vercel.com](https://vercel.com)
2. Sélectionnez votre projet
3. Cliquez sur **"Functions"** pour voir les logs des exécutions

### Debugging

Si le déploiement échoue :
1. Vérifiez les logs de build
2. Vérifiez que tous les fichiers sont commités
3. Vérifiez la structure des imports Python

---

## Mise à Jour du Déploiement

### Déploiement Automatique (Recommandé)

Vercel redéploie automatiquement à chaque push sur la branche `main` :

```bash
git add .
git commit -m "Update: amélioration du générateur"
git push origin main
```

### Déploiement Manuel

```bash
vercel --prod
```

---

## Checklist de Déploiement

- [ ] Repository Git créé et poussé
- [ ] Compte Vercel créé
- [ ] Fichier `vercel.json` présent
- [ ] Fichier `requirements.txt` à la racine
- [ ] Imports Python corrigés (pas de chemins relatifs)
- [ ] Tests locaux réussis
- [ ] Projet importé dans Vercel
- [ ] Premier déploiement réussi
- [ ] URL de production testée
- [ ] Documentation mise à jour avec la nouvelle URL

---

## Coûts

**Vercel Plan Gratuit** :
- ✅ Déploiements illimités
- ✅ 100 GB de bande passante/mois
- ✅ Fonctions serverless incluses
- ⚠️ Timeout de 10 secondes

**Si dépassement** :
- Plan Pro : 20$/mois
- Timeout : 60 secondes

---

## Support

### Documentation Officielle
- [Vercel Python Functions](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel Configuration](https://vercel.com/docs/configuration)

### En Cas de Problème
1. Vérifier les logs Vercel
2. Tester localement avec `vercel dev`
3. Vérifier la compatibilité des dépendances

---

**Bon déploiement ! 🚀**
