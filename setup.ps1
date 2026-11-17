# Sky Vision Group Consultancy - PowerShell Setup Script
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "  Sky Vision Group Consultancy - Django Project Setup" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python
Write-Host "[1/7] Checking Python installation..." -ForegroundColor Yellow
try {
    $pyVersion = python --version 2>&1
    Write-Host "Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Error "Python is not found in PATH! Please install Python 3.10+."
    exit 1
}

# 2. Virtual Environment
Write-Host "`n[2/7] Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment in ./venv ..."
    python -m venv venv
} else {
    Write-Host "Virtual environment already exists in ./venv." -ForegroundColor Green
}

# 3. Activate Virtual Environment
Write-Host "`n[3/7] Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
}

# 4. Install Dependencies
Write-Host "`n[4/7] Installing dependencies from requirements.txt..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Directories and .env
Write-Host "`n[5/7] Checking directories and environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path "media/uploads/resumes")) { New-Item -ItemType Directory -Force -Path "media/uploads/resumes" | Out-Null }
if (-not (Test-Path "database")) { New-Item -ItemType Directory -Force -Path "database" | Out-Null }
if (-not (Test-Path "staticfiles")) { New-Item -ItemType Directory -Force -Path "staticfiles" | Out-Null }
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
}

# 6. Migrations
Write-Host "`n[6/7] Running database migrations..." -ForegroundColor Yellow
python manage.py makemigrations accounts candidates companies internships placements enquiries jobs
python manage.py migrate

# 7. System Check
Write-Host "`n[7/7] Running Django system check..." -ForegroundColor Yellow
python manage.py check

Write-Host "`n==============================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Sky Vision Django Project is Ready!" -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Green
Write-Host "`nTo start the development server:"
Write-Host "  .\venv\Scripts\activate" -ForegroundColor White
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host "`nWebsite URL:   http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "Admin Panel:   http://127.0.0.1:8000/admin-panel/login/" -ForegroundColor Cyan
Write-Host "Django Admin:  http://127.0.0.1:8000/django-admin/" -ForegroundColor Cyan
Write-Host ""
