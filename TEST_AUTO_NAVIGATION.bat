@echo off
echo ================================================================
echo TEST: AUTOMATIC MULTI-LEVEL NAVIGATION
echo ================================================================
echo.
echo This will test the NEW automatic navigation system:
echo - Navigate to music root (multi-level: ROOT -^> Explorer -^> Music Folders)
echo - Navigate to House folder (position 24)
echo - Navigate to Dub folder (position 12)
echo - Test Techno -^> House mapping
echo.
echo REQUIREMENTS:
echo [x] Traktor Pro 3 RUNNING
echo [x] Browser can be at ANY position
echo [x] loopMIDI running
echo [x] ASIO driver active
echo.
pause

.\venv\Scripts\python.exe test_auto_navigation_complete.py

echo.
echo ================================================================
pause
