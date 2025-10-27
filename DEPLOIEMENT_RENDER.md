# 🚀 Guide de Déploiement sur Render.com

## Pourquoi Render ?

✅ **Pas de limite de timeout** - Parfait pour la génération de parcours (10-20s)
✅ **100% gratuit** pour un projet
✅ **Déploiement automatique** depuis GitHub
✅ **Pas de carte bancaire requise**
✅ **SSL gratuit**

---

## 📋 Prérequis

1. **Compte GitHub** : [github.com](https://github.com)
2. **Compte Render** : [render.com](https://render.com) (gratuit)
3. **Git installé** sur votre machine

---

## 🎯 Étape 1 : Créer un Repository GitHub

### Option A : Avec GitHub CLI (recommandé)

```bash
# Se placer dans le dossier du projet
cd c:\Users\rouyc\Documents\testmap

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - Strava+Coach POC"

# Créer le repository GitHub et pousser
gh repo create strava-coach-poc --public --source=. --push
```

### Option B : Manuel (sans GitHub CLI)

```bash
# Se placer dans le dossier du projet
cd c:\Users\rouyc\Documents\testmap

# Initialiser Git
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - Strava+Coach POC"
```

Puis :
1. Allez sur [github.com/new](https://github.com/new)
2. Nom du repo : `strava-coach-poc`
3. Public
4. Cliquez "Create repository"
5. Suivez les instructions pour pousser le code :

```bash
git remote add origin https://github.com/VOTRE_USERNAME/strava-coach-poc.git
git branch -M main
git push -u origin main
```

---

## 🎯 Étape 2 : Déployer sur Render

### 2.1 Créer un compte Render

1. Allez sur [render.com](https://render.com)
2. Cliquez sur **"Get Started"**
3. Connectez-vous avec **GitHub** (recommandé)
4. Autorisez Render à accéder à vos repositories

### 2.2 Créer un Web Service

1. Dans le dashboard Render, cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Cliquez sur **"Connect a repository"** si nécessaire
4. Cherchez et sélectionnez votre repo **`strava-coach-poc`**
5. Cliquez **"Connect"**

### 2.3 Configurer le Service

Remplissez le formulaire avec ces valeurs :

**Basic Information :**
- **Name** : `strava-coach-poc` (ou un nom unique)
- **Region** : `Frankfurt (EU Central)` (choisir le plus proche)
- **Branch** : `main`
- **Root Directory** : (laisser vide)

**Build & Deploy :**
- **Runtime** : `Python 3`
- **Build Command** :
  ```
  pip install -r requirements.txt
  ```
- **Start Command** :
  ```
  cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

**Plan :**
- Sélectionnez **"Free"** (0$/mois)

### 2.4 Variables d'Environnement (Optionnel)

Pour l'instant, pas besoin. Cliquez sur **"Create Web Service"**

---

## 🎯 Étape 3 : Attendre le Déploiement

### Ce qui se passe :

1. **Building** (2-3 minutes) :
   - Installation de Python
   - Installation des dépendances (`requirements.txt`)
   - Compilation si nécessaire

2. **Deploying** (30 secondes) :
   - Lancement du serveur
   - Vérification de santé

3. **Live** ✅ :
   - Votre application est en ligne !

### Voir les Logs

Pendant le déploiement, vous verrez les logs en temps réel dans l'onglet **"Logs"**.

Vous devriez voir :
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

---

## 🎯 Étape 4 : Tester Votre Application

### URL de votre application

Render vous donne une URL automatique :
```
https://strava-coach-poc.onrender.com
```

### Tester l'API

```bash
curl https://strava-coach-poc.onrender.com/health
```

**Réponse attendue :**
```json
{"status": "healthy"}
```

### Tester la génération de parcours

```bash
curl -X POST "https://strava-coach-poc.onrender.com/api/generate-route" \
  -H "Content-Type: application/json" \
  -d '{
    "start_location": "Tour Eiffel, Paris",
    "distance_km": 10.0,
    "training_type": "endurance",
    "elevation_preference": "plat"
  }'
```

### Accéder à l'Interface Web

Ouvrez votre navigateur sur :
```
https://strava-coach-poc.onrender.com/app
```

---

## 🎯 Étape 5 : Configuration Post-Déploiement

### Ajouter un Domaine Personnalisé (Optionnel)

1. Allez dans **Settings** → **Custom Domain**
2. Ajoutez votre domaine (ex: `coach.monsite.com`)
3. Configurez les DNS selon les instructions

### Activer les Déploiements Automatiques

**Déjà activé par défaut !** Chaque fois que vous poussez sur GitHub :

```bash
git add .
git commit -m "Amélioration du générateur"
git push origin main
```

Render redéploie automatiquement en 2-3 minutes.

---

## 📊 Dashboard Render

### Informations Utiles

Dans le dashboard, vous trouverez :

- **Metrics** : CPU, RAM, requêtes/min
- **Logs** : Logs en temps réel
- **Events** : Historique des déploiements
- **Settings** : Configuration du service
- **Environment** : Variables d'environnement

### ⚠️ Limitation du Plan Gratuit

**Le service s'endort après 15 minutes d'inactivité.**

**Impact :**
- Premier appel après sommeil : 30-60 secondes de démarrage
- Appels suivants : instantanés

**Solution pour une démo :**
- Appelez l'URL 2 minutes avant votre présentation
- Le service sera "chaud" et répondra instantanément

---

## 🔧 Maintenance et Mises à Jour

### Voir les Logs en Direct

Dans le dashboard Render :
1. Sélectionnez votre service
2. Cliquez sur **"Logs"**
3. Voyez les requêtes en temps réel

### Redéployer Manuellement

Si besoin de forcer un redéploiement :
1. Allez dans **"Manual Deploy"**
2. Cliquez **"Deploy latest commit"**

### Rollback (Retour Arrière)

Si un déploiement pose problème :
1. Allez dans **"Events"**
2. Trouvez un déploiement précédent qui fonctionnait
3. Cliquez **"Rollback to this version"**

---

## 🐛 Troubleshooting

### Erreur : "Build failed"

**Cause :** Dépendances manquantes

**Solution :**
```bash
# Vérifiez que requirements.txt est à jour
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

### Erreur : "Application failed to start"

**Vérifiez les logs** pour voir l'erreur exacte.

**Causes fréquentes :**
- Port incorrect (utilisez `$PORT` pas `8000`)
- Chemin de démarrage incorrect
- Import Python qui échoue

### Timeout / Lenteur

**Première requête après sommeil : normal (30-60s)**

Pour un service toujours actif :
- Plan payant Render (7$/mois)
- OU utiliser un "keep-alive" service (pinguer toutes les 10 min)

### "Module not found"

```bash
# Assurez-vous que tous les __init__.py existent
touch backend/__init__.py
touch backend/services/__init__.py
touch backend/utils/__init__.py

git add .
git commit -m "Add __init__.py files"
git push
```

---

## 💰 Coûts

### Plan Gratuit (Actuel)
- ✅ 750 heures/mois (suffisant pour un POC)
- ✅ Service s'endort après 15 min inactivité
- ✅ 100 GB de bande passante/mois
- ✅ SSL gratuit

### Plan Starter (7$/mois)
- ✅ Service toujours actif
- ✅ 400 heures d'exécution
- ✅ Meilleur pour une démo/production

---

## 📚 Ressources

- **Dashboard** : [dashboard.render.com](https://dashboard.render.com)
- **Documentation** : [render.com/docs](https://render.com/docs)
- **Status** : [status.render.com](https://status.render.com)
- **Support** : support@render.com

---

## ✅ Checklist de Déploiement

- [ ] Repository GitHub créé
- [ ] Code poussé sur GitHub
- [ ] Compte Render créé
- [ ] Web Service configuré
- [ ] Déploiement réussi (statut "Live")
- [ ] Test API `/health` fonctionne
- [ ] Test génération de parcours fonctionne
- [ ] Interface web `/app` accessible
- [ ] URL partagée avec l'équipe

---

## 🎉 Félicitations !

Votre POC est maintenant en ligne et accessible à tous !

**URL :** `https://strava-coach-poc.onrender.com/app`

**Documentation API :** `https://strava-coach-poc.onrender.com/docs`

---

**Besoin d'aide ? Consultez les logs dans le dashboard Render ou contactez le support.**
