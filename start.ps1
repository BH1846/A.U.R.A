# Quick Start Script for AURA (ASCII-only)
# Run this script to quickly set up and start both backend and frontend

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "AURA - Quick Start Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# If a marker file exists, run non-interactively
if (Test-Path '.skip-prompts') { $env:SKIP_PROMPTS = '1' }

# Create .env from example if missing
if (-not (Test-Path 'backend\.env')) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item 'backend\.env.example' 'backend\.env'
    Write-Host "[OK] .env file created" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit backend\.env and add your OpenAI API key!" -ForegroundColor Red
    Write-Host "Press any key to open .env file..." -ForegroundColor Yellow
    if (-not $env:SKIP_PROMPTS) {
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        notepad 'backend\.env'
    } else {
        Write-Host "(Skipping interactive .env edit)" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "Setting up backend..." -ForegroundColor Cyan
Set-Location -Path 'backend'

if (-not (Test-Path 'venv')) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

Write-Host "[OK] Backend setup complete" -ForegroundColor Green
Set-Location -Path ..

Write-Host "Setting up frontend..." -ForegroundColor Cyan
Set-Location -Path 'frontend'
if (-not (Test-Path 'node_modules')) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install --silent
    Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green
}
Set-Location -Path ..

Write-Host "Starting backend and frontend in new windows..." -ForegroundColor Cyan
$backendPath = (Resolve-Path .\backend).Path
$frontendPath = (Resolve-Path .\frontend).Path
$backendCmd = "Set-Location -Path `"$backendPath`"; .\venv\Scripts\Activate.ps1; python main.py"
$frontendCmd = "Set-Location -Path `"$frontendPath`"; npm run dev"
Start-Process powershell -ArgumentList '-NoExit','-Command',$backendCmd
Start-Process powershell -ArgumentList '-NoExit','-Command',$frontendCmd

Write-Host "AURA is starting. Backend: http://localhost:8000  Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host ""
if (-not $env:SKIP_PROMPTS) { Write-Host 'Press any key to exit this window...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') } else { Write-Host '(Non-interactive run; exiting)' -ForegroundColor Gray }
