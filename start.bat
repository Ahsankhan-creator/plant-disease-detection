@echo off
echo ========================================
echo   PlantGuard AI - Starting Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo Checking model files...
if not exist "agri-plant-disease-resnet50" (
    echo ERROR: Model directory not found!
    echo Please run: git clone https://huggingface.co/mesabo/agri-plant-disease-resnet50
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Server will start on: http://localhost:5000
echo ========================================
echo.
echo Tips:
echo   - Upload clear photos of plant leaves
echo   - Ask questions about plant diseases
echo   - Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

python app.py

pause
