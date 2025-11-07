# Windows PowerShell Setup Script
Write-Host "Setting up tubbyAI Backend..." -ForegroundColor Green

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "✅ Created .env file" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env and add your OPENAI_API_KEY!" -ForegroundColor Red
    } else {
        Write-Host "⚠️  .env.example not found. Creating basic .env..." -ForegroundColor Yellow
        @"
# LLM Configuration
OPENAI_API_KEY=sk-your-openai-key-here
LLM_MODEL=gpt-4

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
"@ | Out-File -FilePath .env -Encoding utf8
        Write-Host "✅ Created .env file" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env and add your OPENAI_API_KEY!" -ForegroundColor Red
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Edit .env and add your OPENAI_API_KEY" -ForegroundColor Cyan
Write-Host "2. Run: python -m app.main" -ForegroundColor Cyan
Write-Host ""

