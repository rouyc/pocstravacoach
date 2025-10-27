# 🚀 Étapes de Déploiement sur Render - Guide Rapide

## ✅ Ce qui est déjà fait

- [x] Projet complété et fonctionnel localement
- [x] Git initialisé
- [x] Premier commit créé
- [x] Fichiers de configuration Render créés (`render.yaml`, `runtime.txt`)

---

## 📝 À FAIRE MAINTENANT

### Étape 1 : Créer un Repository GitHub (5 minutes)

**Option A : Avec GitHub CLI (plus rapide)**
```bash
gh repo create strava-coach-poc --public --source=. --push
```

**Option B : Manuellement**

1. Allez sur [github.com/new](https://github.com/new)
2. Nom du repository : `strava-coach-poc`
3. Public ou Private (votre choix)
4. **NE PAS** cocher "Initialize with README"
5. Cliquez "Create repository"

6. Dans votre terminal, exécutez :
```bash
git remote add origin https://github.com/VOTRE_USERNAME/strava-coach-poc.git
git branch -M main
git push -u origin main
```

---

### Étape 2 : Déployer sur Render (3 minutes)

1. **Créer un compte Render**
   - Allez sur [render.com](https://render.com)
   - Cliquez "Get Started"
   - **Connectez-vous avec GitHub** (plus simple)

2. **Créer un Web Service**
   - Cliquez "New +" → "Web Service"
   - Sélectionnez votre repo `strava-coach-poc`
   - Cliquez "Connect"

3. **Configuration du Service**

   Remplissez comme suit :

   | Champ | Valeur |
   |-------|--------|
   | **Name** | `strava-coach-poc` |
   | **Region** | `Frankfurt (EU Central)` |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | **Plan** | **Free** |

4. **Créer le Service**
   - Cliquez "Create Web Service"
   - Attendez 2-3 minutes ⏱️

---

### Étape 3 : Tester (1 minute)

**Votre URL sera :**
```
https://strava-coach-poc.onrender.com
```

**Tester l'API :**
```bash
curl https://strava-coach-poc.onrender.com/health
```

**Tester l'interface web :**
Ouvrez dans votre navigateur :
```
https://strava-coach-poc.onrender.com/app
```

---

## 🎯 Résumé des Commandes

### Si vous avez GitHub CLI :
```bash
# Pousser sur GitHub
gh repo create strava-coach-poc --public --source=. --push

# C'est tout ! Continuez avec Render.com
```

### Si vous n'avez pas GitHub CLI :
```bash
# Après avoir créé le repo sur github.com :
git remote add origin https://github.com/VOTRE_USERNAME/strava-coach-poc.git
git branch -M main
git push -u origin main
```

---

## ⚠️ Points Importants

### Après 15 min d'inactivité
Le service gratuit Render s'endort. Le premier appel prendra 30-60 secondes.

**Pour une démo :** Ouvrez l'URL 2 minutes avant pour "réchauffer" le service.

### Déploiement automatique
Chaque `git push` redéploie automatiquement ! 🎉

```bash
git add .
git commit -m "Amélioration"
git push
```

---

## 📊 Checklist Complète

- [ ] Repository GitHub créé
- [ ] Code poussé sur GitHub (`git push`)
- [ ] Compte Render créé (via GitHub)
- [ ] Web Service créé sur Render
- [ ] Configuration correcte (Build + Start command)
- [ ] Déploiement réussi (statut "Live" sur Render)
- [ ] Test `/health` → `{"status": "healthy"}`
- [ ] Test `/app` → Interface s'affiche
- [ ] Test génération de parcours → Fonctionne

---

## 🆘 Besoin d'Aide ?

### Problème de Push GitHub
```bash
# Vérifier la configuration
git remote -v

# Si pas de remote configuré
git remote add origin https://github.com/USERNAME/strava-coach-poc.git
```

### Problème de Build Render
- Consultez les **Logs** dans le dashboard Render
- Vérifiez que `requirements.txt` est bien à la racine

### Problème de Start
- Vérifiez que la Start Command est exacte :
  ```
  cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
  ```

---

## 📚 Guides Complets

- **Guide détaillé** : [DEPLOIEMENT_RENDER.md](DEPLOIEMENT_RENDER.md)
- **Documentation** : [render.com/docs](https://render.com/docs)

---

## 🎉 Une fois Déployé

**Partagez votre URL :**
```
https://strava-coach-poc.onrender.com/app
```

**Documentation API auto-générée :**
```
https://strava-coach-poc.onrender.com/docs
```

---

**Bon déploiement ! 🚀**

**Temps total estimé : 10 minutes**
