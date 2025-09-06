@echo off
echo Starting Game Text Translator...
echo.

REM Try to run the launcher first
python launcher.py
if errorlevel 1 (
    echo.
    echo Launcher failed, trying direct run...
    python game_translator.py
    if errorlevel 1 (
        echo.
        echo Both launcher and direct run failed.
        echo Please check that Python is installed.
        pause
    )
)

pause
