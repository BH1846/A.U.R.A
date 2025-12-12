# AURA Production Readiness Checklist

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `.env.production.example` to `.env`
- [ ] Set `DATABASE_URL` with Neon PostgreSQL connection string
- [ ] Add `OPENAI_API_KEY` for GPT-4 evaluation
- [ ] Add `GITHUB_TOKEN` for repository access
- [ ] Generate and set `SECRET_KEY` (use: `openssl rand -hex 32`)
- [ ] Configure `CORS_ORIGINS` with your domain(s)
- [ ] Set production file paths in `REPOS_DIR`, `REPORTS_DIR`, etc.
- [ ] Review and adjust `RATE_LIMIT_PER_MINUTE` settings
- [ ] Set `LOG_LEVEL` to `INFO` or `WARNING` for production

### 2. Infrastructure Setup
- [ ] Docker and Docker Compose installed on server
- [ ] Nginx installed (if using reverse proxy)
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] Domain DNS configured to point to server
- [ ] Firewall configured (ports 80, 443 open)
- [ ] Required directories created with proper permissions:
  ```bash
  sudo mkdir -p /var/www/aura/data/{repos,reports,temp,vector_db}
  sudo chown -R $USER:$USER /var/www/aura
  ```

### 3. Security Hardening
- [ ] All API keys stored in `.env` (not committed to git)
- [ ] `.env` file permissions set to 600 (`chmod 600 .env`)
- [ ] HTTPS enabled with valid SSL certificate
- [ ] Rate limiting configured in nginx
- [ ] CORS origins restricted to production domains only
- [ ] Database connection uses SSL (`?sslmode=require`)
- [ ] Security headers configured in nginx
- [ ] Fail2ban configured for SSH protection

### 4. Database Setup
- [ ] Neon PostgreSQL database created
- [ ] Database connection string tested
- [ ] Database migrations applied (if any)
- [ ] Backup strategy configured
- [ ] Database user has appropriate permissions
- [ ] Connection pooling settings optimized

### 5. Testing Before Deployment
- [ ] Run local Docker build test: `.\scripts\test-docker.ps1`
- [ ] Verify health endpoint responds: `http://localhost:8000/health`
- [ ] Test complete candidate workflow locally
- [ ] Check all API endpoints respond correctly
- [ ] Verify file uploads and downloads work
- [ ] Test report generation (PDF and JSON)
- [ ] Review Docker logs for errors
- [ ] Performance test with multiple concurrent requests

### 6. Production Deployment
- [ ] Build Docker image: `docker build -t aura:latest .`
- [ ] Tag image for registry (if using): `docker tag aura:latest registry.com/aura:latest`
- [ ] Push to registry (if using): `docker push registry.com/aura:latest`
- [ ] Transfer `.env` file to server securely (use scp or similar)
- [ ] Start containers: `docker-compose up -d`
- [ ] Verify containers are running: `docker-compose ps`
- [ ] Check logs: `docker-compose logs -f`
- [ ] Test health endpoint on production domain
- [ ] Verify HTTPS works correctly

### 7. Nginx Configuration
- [ ] Copy `nginx.conf` to `/etc/nginx/sites-available/aura`
- [ ] Update `server_name` with your domain
- [ ] Configure SSL certificate paths
- [ ] Enable site: `sudo ln -s /etc/nginx/sites-available/aura /etc/nginx/sites-enabled/`
- [ ] Test nginx config: `sudo nginx -t`
- [ ] Reload nginx: `sudo systemctl reload nginx`
- [ ] Verify reverse proxy works

### 8. Monitoring & Logging
- [ ] Set up log rotation for Docker logs
- [ ] Configure application logging to external service (optional)
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- [ ] Configure error tracking (Sentry, optional)
- [ ] Set up email/Slack alerts for critical errors
- [ ] Monitor disk space for report/temp directories
- [ ] Set up database monitoring (Neon dashboard)

### 9. Backup & Recovery
- [ ] Document database backup procedure
- [ ] Test database restore procedure
- [ ] Back up generated reports regularly
- [ ] Document disaster recovery plan
- [ ] Store backups in different location (S3, etc.)
- [ ] Test full system restore from backup

### 10. Documentation
- [ ] Update README with production deployment info
- [ ] Document all environment variables
- [ ] Create runbook for common issues
- [ ] Document backup/restore procedures
- [ ] Create incident response plan
- [ ] Document monitoring and alerting setup

### 11. Post-Deployment Verification
- [ ] Access application via production domain
- [ ] Submit test candidate with GitHub URL
- [ ] Verify questions are generated
- [ ] Submit answers and check evaluation
- [ ] Generate and download report
- [ ] Check dashboard displays candidates correctly
- [ ] Monitor logs for 24 hours for errors
- [ ] Load test with expected traffic volume
- [ ] Verify rate limiting works
- [ ] Test CORS with actual frontend domain

### 12. Maintenance Planning
- [ ] Schedule regular security updates
- [ ] Plan for database maintenance windows
- [ ] Set up automated SSL certificate renewal
- [ ] Schedule regular backup verification
- [ ] Plan capacity monitoring and scaling
- [ ] Document update/rollback procedures

## Quick Commands Reference

### Local Testing
```powershell
# Build and test locally
.\scripts\test-docker.ps1

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build
```

### Production Deployment
```bash
# Build image
docker build -t aura:latest .

# Start production
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart service
docker-compose restart

# Update after code changes
docker-compose down
docker build -t aura:latest .
docker-compose up -d
```

### Troubleshooting
```bash
# Check container health
docker-compose exec aura curl http://localhost:8000/health

# Access container shell
docker-compose exec aura /bin/bash

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Check disk space
df -h

# Check database connectivity
docker-compose exec aura python -c "from models import get_db; db = next(get_db()); print('Connected')"
```

## Success Criteria

Your AURA system is production-ready when:
- ✅ All checklist items above are completed
- ✅ Health endpoint returns "healthy" status
- ✅ Complete candidate workflow tested in production
- ✅ HTTPS enabled with valid certificate
- ✅ Monitoring and alerting configured
- ✅ Logs show no critical errors for 24 hours
- ✅ Backup and restore procedures tested
- ✅ Team trained on deployment and maintenance procedures

## Support

For issues during deployment:
1. Check container logs: `docker-compose logs -f`
2. Verify .env configuration matches `.env.production.example`
3. Check nginx error logs: `/var/log/nginx/error.log`
4. Verify database connectivity from container
5. Check disk space and permissions on data directories
6. Review DEPLOYMENT.md for detailed setup instructions
