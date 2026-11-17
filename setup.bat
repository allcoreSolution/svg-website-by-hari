@echo off
setlocal enabledelayedexpansion

echo ==============================================================
echo   Sky Vision Group Consultancy - Django Project Setup (Windows)
echo ==============================================================
echo.

:: 1. Check Python
echo [1/8] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your PATH!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version

:: 2. Create Virtual Environment
echo.
echo [2/8] Setting up Python virtual environment...
if not exist "venv" (
    echo Creating virtual environment in ./venv ...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists in ./venv.
)

:: 3. Activate Virtual Environment
echo.
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [WARNING] Could not activate venv directly. Continuing with system python...
)

:: 4. Upgrade pip
echo.
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip

:: 5. Install Requirements
echo.
echo [5/8] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

:: 6. Create Media & Database Directories
echo.
echo [6/8] Ensuring required directories exist...
if not exist "media\uploads\resumes" mkdir "media\uploads\resumes"
if not exist "database" mkdir "database"
if not exist "staticfiles" mkdir "staticfiles"
if not exist ".env" (
    echo Copying .env.example to .env ...
    copy .env.example .env >nul
)

:: 7. Run Migrations
echo.
echo [7/8] Running Django database migrations...
python manage.py makemigrations accounts candidates companies internships placements enquiries jobs
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Database migration failed!
    pause
    exit /b 1
)

:: 8. Collect Static Files (Optional for dev, good for verification)
echo.
echo [8/8] Checking static files...
python manage.py check

echo.
echo ==============================================================
echo   SUCCESS! Sky Vision Django Project is Ready!
echo ==============================================================
echo.
echo To start the local server:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Website URL:        http://127.0.0.1:8000/
echo Admin Panel:        http://127.0.0.1:8000/admin-panel/login/
echo Django Admin:       http://127.0.0.1:8000/django-admin/
echo.
pause
