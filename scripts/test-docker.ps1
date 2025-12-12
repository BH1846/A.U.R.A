# ============================================
# Docker Build and Test Script for AURA
# ============================================
# This script tests the Docker build locally before deploying to production

Write-Host "=== AURA Docker Build Test ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker status..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker is running" -ForegroundColor Green
Write-Host ""

# Check if .env file exists
Write-Host "Checking environment file..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found." -ForegroundColor Red
    Write-Host "Please copy .env.production.example to .env and configure it." -ForegroundColor Red
    exit 1
}
Write-Host "✓ .env file found" -ForegroundColor Green
Write-Host ""

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>&1 | Out-Null
Write-Host "✓ Cleaned up existing containers" -ForegroundColor Green
Write-Host ""

# Build the Docker image
Write-Host "Building Docker image..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first build..." -ForegroundColor Cyan
docker build -t aura:test .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker build failed. Check the output above for errors." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker image built successfully" -ForegroundColor Green
Write-Host ""

# Start containers with docker-compose
Write-Host "Starting containers with docker-compose..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start containers." -ForegroundColor Red
    exit 1
}
Write-Host "✓ Containers started" -ForegroundColor Green
Write-Host ""

# Wait for services to be ready
Write-Host "Waiting for services to be ready (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check container status
Write-Host "Checking container status..." -ForegroundColor Yellow
docker-compose ps

# Test health endpoint
Write-Host ""
Write-Host "Testing health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    if ($response.status -eq "healthy") {
        Write-Host "✓ Health check passed" -ForegroundColor Green
        Write-Host "Database: $($response.database)" -ForegroundColor Cyan
        Write-Host "Timestamp: $($response.timestamp)" -ForegroundColor Cyan
    } else {
        Write-Host "WARNING: Health check returned unhealthy status" -ForegroundColor Yellow
        Write-Host $response
    }
} catch {
    Write-Host "ERROR: Health check failed" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Test API endpoint
Write-Host ""
Write-Host "Testing API endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/candidates" -Method Get -TimeoutSec 10
    Write-Host "✓ API endpoint responding" -ForegroundColor Green
    Write-Host "Candidates in database: $($response.Count)" -ForegroundColor Cyan
} catch {
    Write-Host "WARNING: API endpoint test failed" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# Show logs
Write-Host ""
Write-Host "=== Recent Container Logs ===" -ForegroundColor Cyan
docker-compose logs --tail=50

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "The AURA application is now running in Docker." -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop containers:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor Cyan
Write-Host ""
