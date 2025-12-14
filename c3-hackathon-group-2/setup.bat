@echo off
REM Setup script for Personal Finance Coach

echo Setting up Personal Finance Coach...
echo.

REM Check if .env exists
if not exist ".env" (
    copy ".env.example" ".env"
    echo ✓ Created .env file from template
    echo ! Please edit .env and add your API keys
    echo.
) else (
    echo . .env file already exists
    echo.
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
    echo.
) else (
    echo . Virtual environment already exists
    echo.
)

echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Install dependencies: pip install -r requirements.txt
echo 3. Edit .env file with your API keys
echo 4. Start backend: cd backend ^&^& uvicorn main:app --reload
echo.
