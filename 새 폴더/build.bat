@echo off
echo Building Game Text Translator...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install requirements
    pause
    exit /b 1
)

REM Build the C++ extension
echo Building C++ extension...
python setup.py build_ext --inplace
if errorlevel 1 (
    echo Error: Failed to build C++ extension
    echo Falling back to Python-only mode...
    echo.
)

echo.
echo Build complete!
echo.
echo To run the program:
echo   python game_translator.py
echo.
pause
