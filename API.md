# API Reference

Documentation complète des endpoints REST de l'API d'authentification biométrique CI/CD.

## Base URL

```
Production: https://api.your-domain.com
Development: http://localhost:8000
```

## Authentification

Tous les endpoints (sauf register et login) requièrent un JWT token dans le header :

```
Authorization: Bearer <your_jwt_token>
```

---

## 📝 Authentication Endpoints

### POST /api/auth/register

Enregistrer un nouvel utilisateur.

**Body (JSON):**
```json
{
  "username": "string (3-50 chars)",
  "email": "valid@email.com",
  "password": "string (min 8 chars)",
  "full_name": "string (optional)",
  "role": "admin|devops|security_officer",
  "consent_given": true
}
```

**Response 201:**
```json
{
  "id": 1,
  "username": "demo_user",
  "email": "demo@example.com",
  "full_name": "Demo User",
  "role": "devops",
  "is_active": true,
  "is_verified": true,
  "consent_given": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- 400: Username/email already exists, consent not given
- 422: Validation error

---

### POST /api/auth/login

Se connecter et obtenir un JWT token.

**Body (form-data):**
```
username=your_username
password=your_password
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- 401: Invalid credentials
- 403: Account inactive

---

### GET /api/auth/me

Obtenir les informations de l'utilisateur actuel.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": 1,
  "username": "demo_user",
  "email": "demo@example.com",
  "full_name": "Demo User",
  "role": "devops",
  "is_active": true,
  "is_verified": true,
  "consent_given": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### DELETE /api/auth/user/{user_id}

Supprimer un utilisateur et toutes ses données (GDPR right to be forgotten).

**Admin only**

**Response 200:**
```json
{
  "message": "User deleted successfully",
  "success": true
}
```

---

## 🔐 Biometric Endpoints

### POST /api/biometric/enroll

Enrôler des données biométriques pour l'utilisateur actuel.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (form-data):**
```
biometric_type: "face"|"voice"|"fingerprint"
consent_confirmed: true
file: <image or audio file>
```

**Supported formats:**
- Face: JPEG, PNG
- Voice: WAV, FLAC, MP3

**Response 200:**
```json
{
  "success": true,
  "message": "Face enrolled successfully",
  "quality_score": 0.92
}
```

**Errors:**
- 400: Failed to extract features, invalid file
- 403: Consent not given

---

### POST /api/biometric/authenticate

Authentifier l'utilisateur avec des données biométriques.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (form-data):**
```
biometric_type: "face"|"voice"
file: <image or audio file>
```

**Response 200:**
```json
{
  "success": true,
  "authenticated": true,
  "similarity_score": 0.94,
  "message": "Authentication successful"
}
```

**Failed Authentication:**
```json
{
  "success": true,
  "authenticated": false,
  "similarity_score": 0.45,
  "message": "Authentication failed"
}
```

---

## 🚀 CI/CD Endpoints

### POST /api/cicd/request-action

Demander une action CI/CD qui nécessite une approbation biométrique.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "action_type": "deploy|rollback|pipeline_modify",
  "description": "Deploy to production environment",
  "pipeline_id": "12345",
  "environment": "production"
}
```

**Response 200:**
```json
{
  "action_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "message": "Action created. Please approve using biometric authentication.",
  "expires_at": "2024-01-15T15:45:00Z"
}
```

**Note:** Les actions expirent après 15 minutes.

---

### POST /api/cicd/approve-action

Approuver une action CI/CD avec authentification biométrique.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Body (form-data):**
```
action_id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
biometric_type: "face"|"voice"
file: <image or audio file>
```

**Response 200 (Approved):**
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

**Response 200 (Denied):**
```json
{
  "success": false,
  "action_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "denied",
  "approved": false,
  "message": "Biometric verification failed. Action denied.",
  "similarity_score": 0.45
}
```

**Errors:**
- 404: Action not found
- 400: Action expired or already processed

---

### GET /api/cicd/action-status/{action_id}

Vérifier le statut d'une action CI/CD.

**Headers:**
```
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "action_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending|approved|denied",
  "message": "Action is pending",
  "expires_at": "2024-01-15T15:45:00Z"
}
```

---

## 📊 Audit Endpoints

### GET /api/audit/logs

Récupérer tous les logs d'audit (Admin uniquement).

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
skip: int = 0          # Pagination offset
limit: int = 100       # Max records (1-1000)
user_id: int = null    # Filter by user
action_type: string = null  # Filter by type (enrollment, authentication, approval)
```

**Response 200:**
```json
{
  "total": 150,
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "action": "Biometric authentication: face",
      "action_type": "authentication",
      "status": "approved",
      "biometric_type": "face",
      "similarity_score": 0.94,
      "pipeline_id": "12345",
      "timestamp": "2024-01-15T10:30:00Z",
      "details": "Authentication successful"
    },
    ...
  ]
}
```

---

### GET /api/audit/logs/user/{user_id}

Récupérer les logs d'un utilisateur spécifique.

Les utilisateurs peuvent voir leurs propres logs. Les admins peuvent voir tous les logs.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
```
skip: int = 0
limit: int = 100
```

**Response 200:**
```json
{
  "total": 25,
  "logs": [...]
}
```

---

## 🏥 System Endpoints

### GET /

Endpoint racine.

**Response 200:**
```json
{
  "message": "Biometric CI/CD Authentication API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

### GET /health

Health check pour monitoring.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## 🔒 Codes d'erreur

| Code | Description |
|------|-------------|
| 200 | Succès |
| 201 | Créé avec succès |
| 400 | Requête invalide |
| 401 | Non authentifié |
| 403 | Non autorisé (permissions insuffisantes) |
| 404 | Ressource non trouvée |
| 413 | Fichier trop large (max 10MB) |
| 422 | Erreur de validation |
| 500 | Erreur serveur |

---

## 📦 Exemples d'intégration

### Python

```python
import requests

API_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{API_URL}/api/auth/login",
    data={"username": "admin", "password": "password"}
)
token = response.json()["access_token"]

# Enroll biometric
with open("face.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/api/biometric/enroll",
        headers={"Authorization": f"Bearer {token}"},
        data={"biometric_type": "face", "consent_confirmed": "true"},
        files={"file": f}
    )
print(response.json())

# Request CI/CD action
response = requests.post(
    f"{API_URL}/api/cicd/request-action",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "action_type": "deploy",
        "description": "Deploy to prod",
        "pipeline_id": "12345"
    }
)
action_id = response.json()["action_id"]

# Approve action
with open("face.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/api/cicd/approve-action",
        headers={"Authorization": f"Bearer {token}"},
        data={"action_id": action_id, "biometric_type": "face"},
        files={"file": f}
    )
print(response.json())
```

### cURL

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -d "username=admin&password=password" | jq -r '.access_token')

# Enroll
curl -X POST "http://localhost:8000/api/biometric/enroll" \
  -H "Authorization: Bearer $TOKEN" \
  -F "biometric_type=face" \
  -F "consent_confirmed=true" \
  -F "file=@face.jpg"

# Request action
ACTION_ID=$(curl -X POST "http://localhost:8000/api/cicd/request-action" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action_type":"deploy","description":"Deploy","pipeline_id":"12345"}' \
  | jq -r '.action_id')

# Approve
curl -X POST "http://localhost:8000/api/cicd/approve-action" \
  -H "Authorization: Bearer $TOKEN" \
  -F "action_id=$ACTION_ID" \
  -F "biometric_type=face" \
  -F "file=@face.jpg"
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const API_URL = 'http://localhost:8000';

// Login
const login = async () => {
  const response = await axios.post(`${API_URL}/api/auth/login`, 
    new URLSearchParams({
      username: 'admin',
      password: 'password'
    })
  );
  return response.data.access_token;
};

// Enroll
const enroll = async (token) => {
  const form = new FormData();
  form.append('biometric_type', 'face');
  form.append('consent_confirmed', 'true');
  form.append('file', fs.createReadStream('face.jpg'));
  
  const response = await axios.post(
    `${API_URL}/api/biometric/enroll`,
    form,
    { headers: { 
      'Authorization': `Bearer ${token}`,
      ...form.getHeaders()
    }}
  );
  return response.data;
};

// Usage
(async () => {
  const token = await login();
  const result = await enroll(token);
  console.log(result);
})();
```

---

## 📚 Ressources supplémentaires

- **Swagger UI** : `/docs` - Documentation interactive
- **ReDoc** : `/redoc` - Documentation alternative
- **OpenAPI Schema** : `/openapi.json` - Schéma OpenAPI 3.0

---

## 📞 Support

Pour des questions sur l'API :
- Documentation : `/docs`
- GitHub Issues : https://github.com/nohailaamo/TP4-V3/issues
- Email : support@your-domain.com
