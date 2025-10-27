@echo off
REM Vision-Guided Browser Navigation Test
REM
REM This script tests the complete browser navigation workflow with vision AI
REM
REM REQUIREMENTS:
REM 1. Traktor Pro 3 must be running
REM 2. Browser must be visible in Traktor UI (left side)
REM 3. loopMIDI configured with "Traktor MIDI Bus 1"
REM 4. API keys configured in autonomous_dj/config.py

echo ============================================================
echo VISION-GUIDED BROWSER NAVIGATION TEST
echo ============================================================
echo.
echo This will test the complete navigation workflow:
echo   - Claude Vision API to read folder names
echo   - OpenRouter LLM to parse commands
echo   - MIDI control for browser navigation
echo   - Intelligent pathfinding to target folder
echo.
echo MAKE SURE:
echo   [x] Traktor Pro 3 is running
echo   [x] Browser is visible in Traktor UI
echo   [x] loopMIDI is configured
echo.
pause

cd C:\traktor
.\venv\Scripts\python.exe test_browser_navigation.py

pause
