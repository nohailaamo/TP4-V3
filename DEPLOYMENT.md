# Guide de Déploiement

## 📦 Déploiement Local (Développement)

### Prérequis
- Python 3.8+
- pip
- Git

### Installation

```bash
# 1. Cloner le repository
git clone https://github.com/nohailaamo/TP4-V3.git
cd TP4-V3

# 2. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configuration
cp .env.example .env
# Éditer .env avec vos paramètres

# 5. Démarrer le serveur
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Accès : http://localhost:8000/docs

## 🐳 Déploiement Docker

### Option 1 : Docker simple

```bash
# Build l'image
docker build -t biometric-cicd:latest .

# Run le container
docker run -d \
  --name biometric-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/logs:/app/logs \
  -e SECRET_KEY="your-secret-key" \
  -e ENCRYPTION_KEY="your-encryption-key" \
  biometric-cicd:latest
```

### Option 2 : Docker Compose

```bash
# Créer .env avec les variables nécessaires
cp .env.example .env

# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down
```

Services disponibles :
- API : http://localhost:8000
- PostgreSQL : localhost:5432 (si activé)

## ☁️ Déploiement Cloud

### AWS (EC2 + RDS)

#### 1. Préparer l'infrastructure

```bash
# Créer une instance EC2
# - Ubuntu 22.04 LTS
# - t2.medium minimum
# - Security Group : ports 22, 80, 443

# Créer RDS PostgreSQL
# - PostgreSQL 15
# - db.t3.micro minimum
# - Security Group : port 5432 depuis EC2
```

#### 2. Configuration EC2

```bash
# Se connecter à EC2
ssh -i your-key.pem ubuntu@your-ec2-ip

# Installer dépendances
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git

# Cloner le projet
git clone https://github.com/nohailaamo/TP4-V3.git
cd TP4-V3

# Setup environnement
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configuration
cp .env.production .env
nano .env
# Configurer DATABASE_URL avec RDS endpoint
```

#### 3. Service systemd

```bash
# Créer /etc/systemd/system/biometric-api.service
sudo nano /etc/systemd/system/biometric-api.service
```

```ini
[Unit]
Description=Biometric CI/CD Authentication API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/TP4-V3
Environment="PATH=/home/ubuntu/TP4-V3/venv/bin"
ExecStart=/home/ubuntu/TP4-V3/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl enable biometric-api
sudo systemctl start biometric-api
sudo systemctl status biometric-api
```

#### 4. Configuration Nginx

```bash
# Créer /etc/nginx/sites-available/biometric-api
sudo nano /etc/nginx/sites-available/biometric-api
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/biometric-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL avec Let's Encrypt

```bash
# Installer certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat
sudo certbot --nginx -d your-domain.com

# Auto-renouvellement configuré automatiquement
```

### Google Cloud Platform (GCP)

#### Cloud Run (Serverless)

```bash
# 1. Build et push l'image
gcloud builds submit --tag gcr.io/PROJECT_ID/biometric-api

# 2. Deploy sur Cloud Run
gcloud run deploy biometric-api \
  --image gcr.io/PROJECT_ID/biometric-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars SECRET_KEY=your-secret \
  --set-env-vars ENCRYPTION_KEY=your-key \
  --set-cloudsql-instances PROJECT_ID:REGION:INSTANCE
```

### Azure

#### App Service

```bash
# 1. Créer App Service
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name biometric-api \
  --runtime "PYTHON:3.11"

# 2. Configurer variables
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name biometric-api \
  --settings SECRET_KEY=your-secret ENCRYPTION_KEY=your-key

# 3. Deploy
az webapp up \
  --resource-group myResourceGroup \
  --name biometric-api \
  --runtime "PYTHON:3.11"
```

### Heroku

```bash
# 1. Créer Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 2. Créer app Heroku
heroku create biometric-api

# 3. Configurer variables
heroku config:set SECRET_KEY=your-secret
heroku config:set ENCRYPTION_KEY=your-key

# 4. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 5. Deploy
git push heroku main
```

## 🔐 Configuration Post-Déploiement

### 1. Sécurité

```bash
# Générer clés sécurisées
openssl rand -hex 32  # Pour SECRET_KEY
openssl rand -hex 32  # Pour ENCRYPTION_KEY

# Mettre à jour .env ou variables d'environnement
```

### 2. Base de données

```bash
# Initialiser la DB (automatique au démarrage)
# Vérifier les tables
sqlite3 biometric_cicd.db ".tables"
# ou pour PostgreSQL
psql -h localhost -U user -d biometric_cicd -c "\dt"
```

### 3. Créer le premier utilisateur admin

```bash
curl -X POST "https://your-domain.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@your-domain.com",
    "password": "SecurePassword123!",
    "full_name": "System Admin",
    "role": "admin",
    "consent_given": true
  }'
```

### 4. Tester l'API

```bash
# Health check
curl https://your-domain.com/health

# API Docs
open https://your-domain.com/docs
```

## 📊 Monitoring

### Logs

```bash
# Logs systemd
sudo journalctl -u biometric-api -f

# Logs application
tail -f /var/log/biometric-cicd/app.log

# Docker logs
docker logs -f biometric-api
```

### Métriques (Optionnel)

#### Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🔄 Mises à Jour

### Process de mise à jour

```bash
# 1. Backup de la DB
sqlite3 biometric_cicd.db ".backup backup_$(date +%Y%m%d).db"
# ou pg_dump pour PostgreSQL

# 2. Pull les changements
git pull origin main

# 3. Mettre à jour dépendances
pip install -r requirements.txt

# 4. Redémarrer le service
sudo systemctl restart biometric-api

# 5. Vérifier
sudo systemctl status biometric-api
curl https://your-domain.com/health
```

## 🆘 Troubleshooting

### Problème : Service ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u biometric-api -n 50

# Vérifier la configuration
cd /home/ubuntu/TP4-V3
source venv/bin/activate
python main.py
```

### Problème : Erreurs de base de données

```bash
# Vérifier la connexion DB
# Pour PostgreSQL
psql -h endpoint -U user -d dbname

# Recréer les tables
rm biometric_cicd.db  # Seulement SQLite
# Redémarrer l'app pour recréer
```

### Problème : Erreurs d'import

```bash
# Réinstaller les dépendances
pip install --upgrade -r requirements.txt

# Vérifier la version Python
python --version  # Doit être 3.8+
```

## 📞 Support

- Documentation : `/docs` sur l'API
- Issues : GitHub Issues
- Email : support@your-domain.com

## ✅ Checklist de Déploiement

- [ ] Clés secrètes générées et sécurisées
- [ ] Base de données configurée (PostgreSQL recommandé)
- [ ] HTTPS configuré (Let's Encrypt ou certificat)
- [ ] Firewall configuré (ports 80, 443 seulement)
- [ ] Service systemd configuré et activé
- [ ] Nginx configuré comme reverse proxy
- [ ] Logs configurés et rotation activée
- [ ] Monitoring configuré (optionnel)
- [ ] Backups automatiques configurés
- [ ] Variables d'environnement sécurisées
- [ ] Premiers tests effectués
- [ ] Documentation d'exploitation créée
- [ ] Déclaration CNDP effectuée (si applicable)
