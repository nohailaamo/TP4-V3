# Quick Start Guide

## Installation rapide

### 1. Installer les dépendances

```bash
# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer .env et changer les clés secrètes
# SECRET_KEY et ENCRYPTION_KEY doivent être uniques en production
```

### 3. Démarrer le serveur

```bash
# Mode développement
uvicorn main:app --reload

# L'API sera accessible sur http://localhost:8000
# Documentation: http://localhost:8000/docs
```

## Test rapide

### Option 1: Interface Web (Swagger UI)

1. Ouvrir http://localhost:8000/docs
2. Utiliser l'interface pour tester les endpoints
3. Commencer par `/api/auth/register` pour créer un utilisateur

### Option 2: Script de démonstration

```bash
# Utiliser une image de visage du dossier data/faces
python example_workflow.py data/faces/1477812374602827.jpeg

# Ou avec un fichier audio
python example_workflow.py data/voices/1462-170142-0000.flac
```

### Option 3: Commandes curl

```bash
# 1. Enregistrer un utilisateur
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "Admin@123456",
    "full_name": "Admin User",
    "role": "admin",
    "consent_given": true
  }'

# 2. Se connecter
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=Admin@123456"

# Sauvegarder le token retourné dans une variable
TOKEN="votre_token_ici"

# 3. Enrollment biométrique
curl -X POST "http://localhost:8000/api/biometric/enroll" \
  -H "Authorization: Bearer $TOKEN" \
  -F "biometric_type=face" \
  -F "consent_confirmed=true" \
  -F "file=@data/faces/1477812374602827.jpeg"

# 4. Authentification biométrique
curl -X POST "http://localhost:8000/api/biometric/authenticate" \
  -H "Authorization: Bearer $TOKEN" \
  -F "biometric_type=face" \
  -F "file=@data/faces/1477812374602827.jpeg"

# 5. Demander une action CI/CD
curl -X POST "http://localhost:8000/api/cicd/request-action" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "deploy",
    "description": "Deploy to production",
    "pipeline_id": "12345",
    "environment": "production"
  }'

# Sauvegarder l'action_id retourné
ACTION_ID="action_id_ici"

# 6. Approuver l'action avec biométrie
curl -X POST "http://localhost:8000/api/cicd/approve-action" \
  -H "Authorization: Bearer $TOKEN" \
  -F "action_id=$ACTION_ID" \
  -F "biometric_type=face" \
  -F "file=@data/faces/1477812374602827.jpeg"
```

## Endpoints principaux

### Authentication
- `POST /api/auth/register` - Enregistrement utilisateur
- `POST /api/auth/login` - Connexion (JWT)
- `GET /api/auth/me` - Info utilisateur actuel
- `DELETE /api/auth/user/{user_id}` - Suppression utilisateur (GDPR)

### Biométrie
- `POST /api/biometric/enroll` - Enrollment biométrique
- `POST /api/biometric/authenticate` - Authentification biométrique

### CI/CD
- `POST /api/cicd/request-action` - Demander une action
- `POST /api/cicd/approve-action` - Approuver avec biométrie
- `GET /api/cicd/action-status/{action_id}` - Vérifier le statut

### Audit
- `GET /api/audit/logs` - Tous les logs (admin)
- `GET /api/audit/logs/user/{user_id}` - Logs utilisateur

## Troubleshooting

### Problème: "ModuleNotFoundError"
```bash
# S'assurer que toutes les dépendances sont installées
pip install -r requirements.txt
```

### Problème: "Database locked" (SQLite)
```bash
# Supprimer la base de données et redémarrer
rm biometric_cicd.db
uvicorn main:app --reload
```

### Problème: "No face detected"
- Utiliser une image avec un visage clair et bien éclairé
- L'image doit être d'au moins 200x200 pixels
- Le visage doit être frontal

### Problème: Erreur d'importation dlib
```bash
# Sur Ubuntu/Debian
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install dlib

# Sur macOS
brew install cmake
pip install dlib
```

## Prochaines étapes

1. **Configuration production** : Changer les clés secrètes dans `.env`
2. **Base de données** : Migrer vers PostgreSQL pour production
3. **HTTPS** : Configurer un reverse proxy (nginx) avec SSL
4. **Rate limiting** : Ajouter des limites de requêtes
5. **Monitoring** : Intégrer Prometheus/Grafana
6. **CI/CD** : Configurer GitLab CI avec `.gitlab-ci.yml`

## Support

- Documentation complète : Voir `README.md`
- API Docs : http://localhost:8000/docs
- Logs : Consulter `app.log`
