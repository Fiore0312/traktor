@echo off
echo ============================================================
echo VISION WORKFLOW - COMPONENT TEST
echo ============================================================
echo.
echo This will test the Vision-Guided Workflow components.
echo Safe mode: No MIDI execution, just verification.
echo.
echo Make sure Traktor is open before continuing!
echo.
pause

cd C:\traktor
.\venv\Scripts\python.exe test_vision_simple.py

echo.
echo ============================================================
echo Test completed. Check output above.
echo ============================================================
echo.
pause
