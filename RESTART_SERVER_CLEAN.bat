@echo off
REM Clean restart of production server with cache cleanup

echo ============================================================
echo CLEAN RESTART - Production Server
echo ============================================================
echo.

echo [1/4] Killing all Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Cleaning Python cache...
cd C:\traktor
del /s /q __pycache__ >nul 2>&1
del /s /q *.pyc >nul 2>&1
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo [3/4] Verifying MIDI driver has browser methods...
findstr /C:"def browser_expand_collapse" traktor_midi_driver.py >nul
if %errorlevel% equ 0 (
    echo    [OK] browser_expand_collapse found in MIDI driver
) else (
    echo    [ERROR] browser_expand_collapse NOT found!
    pause
    exit /b 1
)

echo [4/4] Starting production server...
echo.
echo Server will start now with FRESH module imports.
echo.
pause

cd C:\traktor
.\venv\Scripts\python.exe -m uvicorn server:app --host 0.0.0.0 --port 8000

pause
