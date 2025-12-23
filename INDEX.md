# 📑 INDEX - Navigation du Projet

## 🚀 Pour Commencer

Nouveau sur ce projet ? Commencez ici :

1. **[README.md](README.md)** - Vue d'ensemble complète du projet
2. **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage rapide (5 min)
3. **[LIVRABLES.md](LIVRABLES.md)** - Résumé des livrables du projet

## 📚 Documentation par Sujet

### Installation & Démarrage
- **[QUICKSTART.md](QUICKSTART.md)** - Installation rapide et premiers pas
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Déploiement en production (AWS, GCP, Azure, Heroku)
- **[Dockerfile](Dockerfile)** - Configuration Docker
- **[docker-compose.yml](docker-compose.yml)** - Orchestration Docker
- **[requirements.txt](requirements.txt)** - Dépendances Python

### Développement
- **[main.py](main.py)** - Application FastAPI principale
- **[example_workflow.py](example_workflow.py)** - Script de démonstration
- **[.env.example](.env.example)** - Configuration développement
- **[.env.production](.env.production)** - Configuration production

### API Documentation
- **[API.md](API.md)** - Référence complète des endpoints avec exemples
- **`/docs`** - Swagger UI (interface interactive) - Disponible quand le serveur tourne
- **`/redoc`** - ReDoc (documentation alternative) - Disponible quand le serveur tourne

### Sécurité & Conformité
- **[SECURITY.md](SECURITY.md)** - Architecture de sécurité et conformité RGPD
- **[app/utils/encryption.py](app/utils/encryption.py)** - Module de chiffrement
- **[app/api/dependencies.py](app/api/dependencies.py)** - Authentification et autorisations

### CI/CD Integration
- **[.gitlab-ci.yml](.gitlab-ci.yml)** - Pipeline GitLab CI avec validation biométrique
- **[README.md#intégration-cicd](README.md#-intégration-cicd)** - Guide d'intégration CI/CD
- **[API.md#cicd-endpoints](API.md#-cicd-endpoints)** - Endpoints CI/CD

## 🏗️ Structure du Code

### Application Backend (`app/`)

#### API Endpoints (`app/api/`)
- **[auth.py](app/api/auth.py)** - Authentification (register, login, JWT)
- **[biometric.py](app/api/biometric.py)** - Enrollment et authentification biométrique
- **[cicd.py](app/api/cicd.py)** - Approbation des actions CI/CD
- **[audit.py](app/api/audit.py)** - Logs d'audit et traçabilité
- **[dependencies.py](app/api/dependencies.py)** - Dépendances, auth, RBAC

#### Core (`app/core/`)
- **[database.py](app/core/database.py)** - Connexion base de données async

#### Models (`app/models/`)
- **[database.py](app/models/database.py)** - Modèles SQLAlchemy (User, BiometricData, AuditLog, CICDAction)
- **[schemas.py](app/models/schemas.py)** - Schémas Pydantic pour validation

#### Services (`app/services/`)
- **[biometric.py](app/services/biometric.py)** - Orchestration des opérations biométriques
- **[face_recognition.py](app/services/face_recognition.py)** - Reconnaissance faciale
- **[voice_recognition.py](app/services/voice_recognition.py)** - Reconnaissance vocale (MFCC)
- **[auth.py](app/services/auth.py)** - Service JWT et authentification

#### Utilities (`app/utils/`)
- **[encryption.py](app/utils/encryption.py)** - Chiffrement AES, pseudonymisation

### Configuration (`config/`)
- **[settings.py](config/settings.py)** - Configuration centralisée avec Pydantic

### Tests (`tests/`)
- **[test_api.py](tests/test_api.py)** - Tests basiques de l'API

## 🎯 Cas d'Usage

### Je veux...

#### ...installer et tester localement
→ **[QUICKSTART.md](QUICKSTART.md)** sections 1-3

#### ...comprendre les endpoints API
→ **[API.md](API.md)** ou `/docs` quand le serveur tourne

#### ...déployer en production
→ **[DEPLOYMENT.md](DEPLOYMENT.md)** pour votre plateforme (AWS, GCP, etc.)

#### ...intégrer avec GitLab CI
→ **[.gitlab-ci.yml](.gitlab-ci.yml)** et **[README.md#gitlab-ci](README.md#gitlab-ci)**

#### ...comprendre la sécurité
→ **[SECURITY.md](SECURITY.md)** (chiffrement, RGPD, conformité)

#### ...modifier le code biométrique
→ **[app/services/face_recognition.py](app/services/face_recognition.py)** ou **[voice_recognition.py](app/services/voice_recognition.py)**

#### ...ajouter un nouvel endpoint
→ Créer dans **[app/api/](app/api/)** + voir **[API.md](API.md)** pour la structure

#### ...changer la configuration
→ Modifier **[.env](.env.example)** ou **[config/settings.py](config/settings.py)**

## 📋 Workflows Typiques

### Workflow 1 : Premier Déploiement

1. Lire **[README.md](README.md)** (vue d'ensemble)
2. Suivre **[QUICKSTART.md](QUICKSTART.md)** (installation)
3. Tester avec **[example_workflow.py](example_workflow.py)**
4. Consulter **[DEPLOYMENT.md](DEPLOYMENT.md)** (production)
5. Configurer **[.gitlab-ci.yml](.gitlab-ci.yml)** (CI/CD)

### Workflow 2 : Développement

1. Comprendre **[app/models/database.py](app/models/database.py)** (modèles)
2. Étudier **[app/services/](app/services/)** (logique métier)
3. Examiner **[app/api/](app/api/)** (endpoints)
4. Tester avec **[tests/test_api.py](tests/test_api.py)**
5. Documenter dans **[API.md](API.md)**

### Workflow 3 : Intégration CI/CD

1. Lire **[.gitlab-ci.yml](.gitlab-ci.yml)** (exemple complet)
2. Comprendre **[app/api/cicd.py](app/api/cicd.py)** (endpoints)
3. Consulter **[API.md#ci/cd-endpoints](API.md#-cicd-endpoints)** (référence)
4. Tester avec **[example_workflow.py](example_workflow.py)**
5. Adapter à votre pipeline

## 🔍 Recherche Rapide

### Par Fonctionnalité

| Fonctionnalité | Fichier Principal | Documentation |
|----------------|-------------------|---------------|
| Reconnaissance faciale | `app/services/face_recognition.py` | README.md |
| Reconnaissance vocale | `app/services/voice_recognition.py` | README.md |
| Chiffrement | `app/utils/encryption.py` | SECURITY.md |
| JWT Auth | `app/services/auth.py` | API.md |
| RBAC | `app/api/dependencies.py` | SECURITY.md |
| Audit logs | `app/models/database.py` (AuditLog) | SECURITY.md |
| CI/CD | `app/api/cicd.py` + `.gitlab-ci.yml` | API.md |
| Base de données | `app/core/database.py` | DEPLOYMENT.md |

### Par Endpoint API

| Endpoint | Fichier | Documentation |
|----------|---------|---------------|
| `/api/auth/*` | `app/api/auth.py` | API.md |
| `/api/biometric/*` | `app/api/biometric.py` | API.md |
| `/api/cicd/*` | `app/api/cicd.py` | API.md |
| `/api/audit/*` | `app/api/audit.py` | API.md |

## 🆘 Support & Ressources

### Documentation
- **Documentation complète** : Tous les fichiers .md
- **API Interactive** : `/docs` (Swagger UI)
- **Schéma OpenAPI** : `/openapi.json`

### Code
- **Exemples d'utilisation** : `example_workflow.py`
- **Tests** : `tests/test_api.py`
- **Configuration** : `.env.example`

### Déploiement
- **Local** : QUICKSTART.md
- **Docker** : Dockerfile + docker-compose.yml
- **Cloud** : DEPLOYMENT.md

### Sécurité
- **Chiffrement** : SECURITY.md
- **RGPD** : SECURITY.md
- **Audit** : SECURITY.md

## 📞 Contacts & Liens

- **Repository** : https://github.com/nohailaamo/TP4-V3
- **Issues** : https://github.com/nohailaamo/TP4-V3/issues
- **Documentation API** : `/docs` (quand serveur actif)

## 🗺️ Plan du Site

```
TP4-V3/
│
├── 📖 Documentation
│   ├── README.md           ← Commencer ici
│   ├── QUICKSTART.md       ← Installation rapide
│   ├── API.md              ← Référence API
│   ├── SECURITY.md         ← Sécurité & RGPD
│   ├── DEPLOYMENT.md       ← Déploiement production
│   ├── LIVRABLES.md        ← Résumé projet
│   └── INDEX.md            ← Ce fichier
│
├── 🔧 Configuration
│   ├── .env.example        ← Config développement
│   ├── .env.production     ← Config production
│   ├── requirements.txt    ← Dépendances Python
│   ├── Dockerfile          ← Image Docker
│   └── docker-compose.yml  ← Orchestration
│
├── 🚀 Application
│   ├── main.py             ← Point d'entrée FastAPI
│   ├── app/                ← Code application
│   │   ├── api/           ← Endpoints REST
│   │   ├── core/          ← Base données
│   │   ├── models/        ← Modèles & schemas
│   │   ├── services/      ← Logique métier
│   │   └── utils/         ← Utilitaires
│   └── config/            ← Configuration
│
├── 🧪 Tests & Exemples
│   ├── tests/             ← Tests unitaires
│   └── example_workflow.py ← Démonstration
│
└── 🔄 CI/CD
    └── .gitlab-ci.yml      ← Pipeline GitLab
```

## ✅ Checklist de Navigation

Pour vérifier que vous avez tout exploré :

- [ ] Lu README.md (vue d'ensemble)
- [ ] Installé via QUICKSTART.md
- [ ] Testé avec example_workflow.py
- [ ] Consulté API.md ou /docs
- [ ] Compris SECURITY.md (sécurité)
- [ ] Exploré le code dans app/
- [ ] Lu DEPLOYMENT.md (si déploiement)
- [ ] Étudié .gitlab-ci.yml (si CI/CD)
- [ ] Consulté LIVRABLES.md (résumé)

---

**💡 Astuce** : Gardez ce fichier INDEX.md ouvert pour naviguer rapidement dans le projet !
