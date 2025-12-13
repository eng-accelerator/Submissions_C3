@echo off
echo Starting Multi-Agent Deep Researcher...
echo.
echo Checking Python version...
python check_python_version.py
if errorlevel 1 (
    echo.
    echo Please install Python 3.9-3.13 to run this project.
    pause
    exit /b 1
)
echo.
echo Ensure you have valid API keys in .env file or the UI.
echo.
streamlit run app.py
pause
