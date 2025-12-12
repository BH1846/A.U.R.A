#!/bin/bash

# ============================================
# Docker Build and Test Script for AURA (Linux/Mac)
# ============================================

set -e  # Exit on error

echo "=== AURA Docker Build Test ==="
echo ""

# Check if Docker is running
echo "Checking Docker status..."
if ! docker ps > /dev/null 2>&1; then
    echo "ERROR: Docker is not running. Please start Docker."
    exit 1
fi
echo "✓ Docker is running"
echo ""

# Check if .env file exists
echo "Checking environment file..."
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found."
    echo "Please copy .env.production.example to .env and configure it."
    exit 1
fi
echo "✓ .env file found"
echo ""

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down > /dev/null 2>&1 || true
echo "✓ Cleaned up existing containers"
echo ""

# Build the Docker image
echo "Building Docker image..."
echo "This may take 5-10 minutes on first build..."
if ! docker build -t aura:test .; then
    echo "ERROR: Docker build failed."
    exit 1
fi
echo "✓ Docker image built successfully"
echo ""

# Start containers with docker-compose
echo "Starting containers with docker-compose..."
if ! docker-compose up -d; then
    echo "ERROR: Failed to start containers."
    exit 1
fi
echo "✓ Containers started"
echo ""

# Wait for services to be ready
echo "Waiting for services to be ready (30 seconds)..."
sleep 30

# Check container status
echo "Checking container status..."
docker-compose ps

# Test health endpoint
echo ""
echo "Testing health endpoint..."
if response=$(curl -s -f http://localhost:8000/health); then
    echo "✓ Health check passed"
    echo "$response" | grep -o '"status":"[^"]*"' || true
    echo "$response" | grep -o '"database":"[^"]*"' || true
else
    echo "WARNING: Health check failed"
fi

# Test API endpoint
echo ""
echo "Testing API endpoint..."
if curl -s -f http://localhost:8000/api/candidates > /dev/null; then
    echo "✓ API endpoint responding"
else
    echo "WARNING: API endpoint test failed"
fi

# Show logs
echo ""
echo "=== Recent Container Logs ==="
docker-compose logs --tail=50

echo ""
echo "=== Test Complete ==="
echo ""
echo "The AURA application is now running in Docker."
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Health Check: http://localhost:8000/health"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop containers:"
echo "  docker-compose down"
echo ""
