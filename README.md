# Biometric CI/CD Authentication System

## 🔐 Vue d'ensemble

Système d'authentification biométrique multimodale pour sécuriser les actions critiques des pipelines CI/CD (GitLab, Jenkins). Avant tout déploiement, rollback ou modification de pipeline, l'administrateur DevOps doit valider son identité par reconnaissance biométrique.

## ✨ Fonctionnalités

### Biométrie
- **Reconnaissance faciale** avec `face_recognition`
- **Reconnaissance vocale** avec `librosa` (extraction MFCC)
- Chiffrement AES-256 des descripteurs biométriques
- Calcul de scores de similarité, FAR, FRR, EER
- Évaluation de qualité des échantillons biométriques

### Sécurité
- Chiffrement des descripteurs avec `cryptography`
- Pseudonymisation des identifiants (SHA-256)
- Authentification JWT/OAuth2
- Gestion des rôles (Admin, DevOps, Security Officer)
- Protection CORS et validation des fichiers

### Traçabilité & Conformité
- Journalisation complète de tous les accès
- Stockage SQLite/PostgreSQL des logs d'audit
- Conformité RGPD/Loi 08.09
- Gestion du consentement utilisateur
- Droit à l'oubli (suppression des données)
- Politique de rétention des données

### Intégration CI/CD
- Endpoints REST pour validation des actions
- Exemple GitLab CI avec étape de validation biométrique
- Blocage automatique en cas d'échec d'authentification
- Support des actions : deploy, rollback, pipeline_modify

## 🏗️ Architecture

```
TP4-V3/
├── app/
│   ├── api/                    # Endpoints REST
│   │   ├── auth.py            # Authentification (register, login)
│   │   ├── biometric.py       # Enrollment et authentification biométrique
│   │   ├── cicd.py            # Approbation des actions CI/CD
│   │   └── audit.py           # Logs d'audit
│   ├── core/
│   │   └── database.py        # Configuration base de données
│   ├── models/
│   │   ├── database.py        # Modèles SQLAlchemy
│   │   └── schemas.py         # Schémas Pydantic
│   ├── services/
│   │   ├── auth.py            # Service d'authentification JWT
│   │   ├── biometric.py       # Orchestration biométrique
│   │   ├── face_recognition.py # Reconnaissance faciale
│   │   └── voice_recognition.py # Reconnaissance vocale
│   └── utils/
│       └── encryption.py      # Chiffrement et pseudonymisation
├── config/
│   └── settings.py            # Configuration de l'application
├── data/                       # Données d'entraînement
│   ├── faces/
│   ├── fingerprint/
│   └── voices/
├── tests/                      # Tests unitaires et d'intégration
├── main.py                     # Application FastAPI principale
├── requirements.txt            # Dépendances Python
├── .gitlab-ci.yml             # Exemple d'intégration GitLab CI
├── .env.example               # Variables d'environnement
└── README.md

```

## 🚀 Installation

### Prérequis

- Python 3.8+
- pip
- (Optionnel) PostgreSQL pour production

### Installation des dépendances

```bash
# Cloner le repository
git clone https://github.com/nohailaamo/TP4-V3.git
cd TP4-V3

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration

```bash
# Copier le fichier de configuration exemple
cp .env.example .env

# Éditer .env avec vos paramètres
nano .env
```

Variables importantes à configurer :
- `SECRET_KEY` : Clé secrète pour JWT (générer avec `openssl rand -hex 32`)
- `ENCRYPTION_KEY` : Clé de chiffrement pour les descripteurs biométriques
- `DATABASE_URL` : URL de connexion à la base de données
- `SIMILARITY_THRESHOLD` : Seuil de similarité (0.85 par défaut)

## 🎯 Utilisation

### Démarrer le serveur

```bash
# Mode développement (avec rechargement automatique)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Mode production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

L'API sera accessible sur `http://localhost:8000`

Documentation interactive :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

### Workflow d'utilisation

#### 1. Enregistrement d'un utilisateur

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_devops",
    "email": "admin@example.com",
    "password": "SecureP@ssw0rd",
    "full_name": "Admin DevOps",
    "role": "admin",
    "consent_given": true
  }'
```

#### 2. Connexion

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin_devops&password=SecureP@ssw0rd"
```

Réponse :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 3. Enrollment biométrique

```bash
# Enrollment facial
curl -X POST "http://localhost:8000/api/biometric/enroll" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "biometric_type=face" \
  -F "consent_confirmed=true" \
  -F "file=@data/faces/face_sample.jpeg"
```

Réponse :
```json
{
  "success": true,
  "message": "Face enrolled successfully",
  "quality_score": 0.92
}
```

#### 4. Authentification biométrique

```bash
curl -X POST "http://localhost:8000/api/biometric/authenticate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "biometric_type=face" \
  -F "file=@data/faces/face_verify.jpeg"
```

Réponse :
```json
{
  "success": true,
  "authenticated": true,
  "similarity_score": 0.94,
  "message": "Authentication successful"
}
```

#### 5. Demande d'action CI/CD

```bash
curl -X POST "http://localhost:8000/api/cicd/request-action" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "deploy",
    "description": "Deploy to production",
    "pipeline_id": "12345",
    "environment": "production"
  }'
```

Réponse :
```json
{
  "action_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Action created. Please approve using biometric authentication.",
  "expires_at": "2024-01-15T15:30:00"
}
```

#### 6. Approbation de l'action avec biométrie

```bash
curl -X POST "http://localhost:8000/api/cicd/approve-action" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "action_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890" \
  -F "biometric_type=face" \
  -F "file=@data/faces/face_approve.jpeg"
```

Réponse (succès) :
```json
{
  "success": true,
  "action_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "approved",
  "approved": true,
  "message": "Action approved successfully. CI/CD pipeline can proceed.",
  "similarity_score": 0.95
}
```

#### 7. Consulter les logs d'audit (Admin uniquement)

```bash
curl -X GET "http://localhost:8000/api/audit/logs?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔄 Intégration CI/CD

### GitLab CI

Le fichier `.gitlab-ci.yml` fourni intègre la validation biométrique dans votre pipeline.

**Étapes clés :**

1. **Configuration des variables** dans GitLab CI/CD :
   - `BIOMETRIC_API_URL` : URL de l'API biométrique
   - `BIOMETRIC_TOKEN` : Token JWT (masqué)

2. **Étape de validation biométrique** :
   - Le pipeline demande une approbation biométrique
   - Affiche l'Action ID
   - Attend l'approbation (max 15 minutes)
   - Bloque le déploiement si refusé

3. **Déploiement** :
   - Ne s'exécute que si l'approbation biométrique est réussie

### Jenkins

Pour Jenkins, créez un stage similaire :

```groovy
stage('Biometric Approval') {
    steps {
        script {
            // Request approval
            def response = sh(
                script: """
                    curl -X POST "${BIOMETRIC_API_URL}/api/cicd/request-action" \
                    -H "Authorization: Bearer ${BIOMETRIC_TOKEN}" \
                    -H "Content-Type: application/json" \
                    -d '{"action_type":"deploy","description":"Deploy to production","pipeline_id":"${BUILD_ID}"}'
                """,
                returnStdout: true
            )
            def actionId = readJSON(text: response).action_id
            
            echo "Action ID: ${actionId}"
            echo "Please approve using biometric authentication"
            
            // Wait for approval
            timeout(time: 15, unit: 'MINUTES') {
                waitUntil {
                    def status = sh(
                        script: "curl -s ${BIOMETRIC_API_URL}/api/cicd/action-status/${actionId} -H 'Authorization: Bearer ${BIOMETRIC_TOKEN}'",
                        returnStdout: true
                    )
                    def statusJson = readJSON(text: status)
                    return statusJson.status == 'approved'
                }
            }
        }
    }
}
```

## 📊 Métriques de performance

### Scores de similarité

- **Face Recognition** : Utilise la distance euclidienne entre embeddings (0-1)
  - Seuil par défaut : 0.6 (configurable via `FACE_RECOGNITION_TOLERANCE`)
  
- **Voice Recognition** : Utilise la similarité cosinus entre vecteurs MFCC
  - Seuil par défaut : 0.85 (configurable via `SIMILARITY_THRESHOLD`)

### Métriques biométriques

- **FAR (False Acceptance Rate)** : Taux de fausses acceptations
- **FRR (False Rejection Rate)** : Taux de faux rejets
- **EER (Equal Error Rate)** : Point où FAR = FRR

Ces métriques sont calculées lors de l'évaluation du système.

## 🔒 Sécurité

### Chiffrement des données

- **Descripteurs biométriques** : Chiffrés avec AES-256 via Fernet
- **Mots de passe** : Hashés avec bcrypt
- **Identifiants** : Pseudonymisés avec SHA-256

### Bonnes pratiques

1. **Ne jamais stocker** les images/audio bruts en production
2. **Utiliser HTTPS** pour toutes les communications
3. **Rotation régulière** des clés de chiffrement
4. **Audits réguliers** des logs d'accès
5. **Limitation du taux** de requêtes (rate limiting)

## 📋 Conformité RGPD

### Article 9 - Données biométriques

- ✅ Consentement explicite requis
- ✅ Minimisation des données
- ✅ Chiffrement des données sensibles
- ✅ Droit à l'oubli implémenté
- ✅ Politique de rétention (365 jours par défaut)
- ✅ Traçabilité complète

### Endpoints de conformité

- `POST /api/auth/register` : Collecte du consentement
- `DELETE /api/auth/user/{user_id}` : Droit à l'oubli
- `GET /api/audit/logs/user/{user_id}` : Accès aux données personnelles

## 🧪 Tests

### Tests unitaires

```bash
# Installer pytest
pip install pytest pytest-asyncio httpx

# Exécuter les tests
pytest tests/ -v
```

### Tests d'intégration

```bash
# Test complet du workflow
pytest tests/test_integration.py -v
```

## 🐛 Dépannage

### Problème : "No face detected"

**Solution** : Assurez-vous que :
- L'image contient un visage clairement visible
- Le visage est bien éclairé
- L'image est de bonne qualité (> 200x200 pixels)

### Problème : "Failed to extract voice features"

**Solution** : Vérifiez que :
- Le fichier audio est au format supporté (WAV, FLAC, MP3)
- La durée audio est suffisante (> 1 seconde)
- Le niveau audio n'est pas trop faible

### Problème : "Authentication failed" avec bon score

**Solution** : Ajustez les seuils dans `.env` :
- `FACE_RECOGNITION_TOLERANCE` : Augmenter pour être moins strict
- `SIMILARITY_THRESHOLD` : Diminuer pour être moins strict

## 📚 Références

### Bibliothèques utilisées

- **FastAPI** : Framework web moderne
- **face_recognition** : Reconnaissance faciale
- **librosa** : Traitement audio et extraction MFCC
- **cryptography** : Chiffrement AES/RSA
- **SQLAlchemy** : ORM pour base de données
- **Pydantic** : Validation des données

### Standards et normes

- **ISO/IEC 19795** : Évaluation des performances biométriques
- **RGPD Article 9** : Traitement des données biométriques
- **Loi 08.09** : Protection des données personnelles (Maroc)

## 🤝 Contribution

Les contributions sont bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

Développé dans le cadre du TP4 - Biométrie et confiance numérique.

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation : `/docs`
- Vérifier les logs : `app.log`

---

**⚠️ Note importante** : Ce système traite des données biométriques sensibles. Assurez-vous de respecter toutes les réglementations locales et internationales sur la protection des données avant de déployer en production.
