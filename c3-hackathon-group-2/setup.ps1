# Create .env file from example
if (-Not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file from template"
    Write-Host "⚠️  Please edit .env and add your API keys"
} else {
    Write-Host "ℹ️  .env file already exists"
}

# Create virtual environment
if (-Not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    Write-Host "✅ Virtual environment created"
} else {
    Write-Host "ℹ️  Virtual environment already exists"
}

# Activate virtual environment
Write-Host "`n📦 Activating virtual environment..."
Write-Host "Run: .\venv\Scripts\activate"
Write-Host "`nThen install dependencies: pip install -r requirements.txt"
Write-Host "Then start backend: cd backend && uvicorn main:app --reload"
