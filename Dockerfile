# Multi-stage build for AURA - Frontend + Backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p /var/www/aura/data/{repos,reports,temp,vector_db,logs}

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Configure nginx to serve frontend and proxy backend
RUN echo 'server { \n\
    listen ${PORT}; \n\
    server_name _; \n\
    root /app/frontend/dist; \n\
    index index.html; \n\
    \n\
    # Serve frontend \n\
    location / { \n\
        try_files $uri $uri/ /index.html; \n\
    } \n\
    \n\
    # Proxy API requests to backend \n\
    location /api/ { \n\
        proxy_pass http://127.0.0.1:8000; \n\
        proxy_http_version 1.1; \n\
        proxy_set_header Upgrade $http_upgrade; \n\
        proxy_set_header Connection "upgrade"; \n\
        proxy_set_header Host $host; \n\
        proxy_set_header X-Real-IP $remote_addr; \n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \n\
        proxy_set_header X-Forwarded-Proto $scheme; \n\
    } \n\
    \n\
    location /health { \n\
        proxy_pass http://127.0.0.1:8000; \n\
    } \n\
}' > /etc/nginx/nginx.conf.template

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
export PORT=${PORT:-10000}\n\
echo "Starting services on port $PORT"\n\
cd /app/backend\n\
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --daemon\n\
sleep 2\n\
envsubst "\$PORT" < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf\n\
cat /etc/nginx/conf.d/default.conf\n\
rm -f /etc/nginx/sites-enabled/default\n\
nginx -g "daemon off;"' > /start.sh && chmod +x /start.sh

WORKDIR /app
CMD ["/start.sh"]
