# 🚀 AURA Production Deployment Guide

## Prerequisites

- Server with at least 2GB RAM and 20GB storage
- Docker and Docker Compose installed
- Domain name with DNS configured
- SSL certificates (Let's Encrypt recommended)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/aura.git
cd aura
```

### 2. Environment Configuration

```bash
# Copy and edit environment file
cp backend/.env.example backend/.env
nano backend/.env
```

**Required Environment Variables:**

```env
# CRITICAL: Change these for production!
OPENAI_API_KEY=your_actual_openai_key
GITHUB_TOKEN=your_github_token
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=["https://yourdomain.com"]
DEBUG=False
```

### 3. Generate Secret Key

```bash
openssl rand -hex 32
```

Copy the output to `SECRET_KEY` in `.env`

### 4. Create Data Directories

```bash
mkdir -p data/{repos,reports,temp,vector_db}
mkdir -p logs
chmod -R 755 data logs
```

### 5. SSL Certificate Setup

**Option A: Let's Encrypt (Recommended)**

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
mkdir -p ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/
sudo chmod 644 ssl/*
```

**Option B: Self-Signed (Development Only)**

```bash
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem -out ssl/fullchain.pem
```

### 6. Update Nginx Configuration

Edit `nginx.conf` and replace `yourdomain.com` with your actual domain.

### 7. Build and Deploy

```bash
# Build Docker image
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f aura
```

### 8. Verify Deployment

```bash
# Check health
curl https://yourdomain.com/health

# Check API
curl https://yourdomain.com/api/roles
```

## Alternative Deployment Methods

### Method 1: Traditional Server (Without Docker)

#### Install Dependencies

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install python3.11 python3.11-venv python3-pip

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Git
sudo apt-get install git
```

#### Setup Backend

```bash
cd /var/www/aura/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

#### Setup Frontend

```bash
cd /var/www/aura/frontend
npm install
npm run build
```

#### Create Systemd Service

Create `/etc/systemd/system/aura.service`:

```ini
[Unit]
Description=AURA Backend Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/aura/backend
Environment="PATH=/var/www/aura/backend/venv/bin"
ExecStart=/var/www/aura/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/www/aura/logs/access.log \
    --error-logfile /var/www/aura/logs/error.log
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable aura
sudo systemctl start aura
sudo systemctl status aura
```

### Method 2: Cloud Platforms

#### Deploy to Render.com

1. Create `render.yaml`:

```yaml
services:
  - type: web
    name: aura
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: GITHUB_TOKEN
        sync: false
```

2. Connect to GitHub and deploy

#### Deploy to Railway

```bash
railway login
railway init
railway add
railway up
```

## Maintenance

### Update Application

```bash
git pull origin main
docker-compose down
docker-compose build
docker-compose up -d
```

### Database Backup

```bash
# Backup Neon PostgreSQL
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Clean Up Old Repositories

```bash
# Add to crontab: 0 2 * * * (runs at 2 AM daily)
find /var/www/aura/data/repos -type d -mtime +7 -exec rm -rf {} +
```

### Monitor Logs

```bash
# Docker
docker-compose logs -f aura

# System service
sudo journalctl -u aura -f

# Nginx
sudo tail -f /var/log/nginx/aura_access.log
sudo tail -f /var/log/nginx/aura_error.log
```

### Resource Monitoring

```bash
# Check disk usage
df -h /var/www/aura/data

# Check memory
free -h

# Check running processes
docker stats  # For Docker
htop          # For system service
```

## Security Best Practices

1. ✅ Change all default credentials
2. ✅ Use HTTPS only (enforce SSL)
3. ✅ Enable rate limiting
4. ✅ Keep secrets in environment variables
5. ✅ Regular security updates
6. ✅ Enable firewall (UFW)
7. ✅ Regular backups
8. ✅ Monitor logs for suspicious activity

## Troubleshooting

### Backend Not Starting

```bash
# Check logs
docker-compose logs aura

# Check environment
docker exec -it aura-production env | grep DATABASE_URL

# Test database connection
docker exec -it aura-production python -c "from models.database import test_connection; test_connection()"
```

### High Memory Usage

```bash
# Reduce workers in .env
WORKERS=2

# Restart
docker-compose restart aura
```

### Disk Space Issues

```bash
# Check usage
du -sh /var/www/aura/data/*

# Clean old repos
find /var/www/aura/data/repos -type d -mtime +3 -exec rm -rf {} +

# Clean old reports
find /var/www/aura/data/reports -type f -mtime +30 -delete
```

## Support

For issues or questions, please open an issue on GitHub.
