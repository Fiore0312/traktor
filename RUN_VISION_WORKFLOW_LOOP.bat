@echo off
echo ============================================================
echo VISION WORKFLOW - AUTONOMOUS LOOP (INFINITE)
echo ============================================================
echo.
echo WARNING: This will run an INFINITE LOOP controlling Traktor!
echo.
echo What this does:
echo   - Continuously capture screenshots
echo   - Analyze UI with Claude Vision
echo   - Execute actions autonomously
echo   - Repeat every 5 seconds
echo.
echo This is FULL AUTONOMOUS DJ MODE!
echo.
echo REQUIREMENTS:
echo   - Traktor Pro 3 OPEN and ready
echo   - Audio interface connected
echo   - loopMIDI "Traktor MIDI Bus 1" active
echo   - Music library loaded in Traktor
echo.
echo To STOP: Press Ctrl+C in this window
echo.
echo Press Ctrl+C NOW to cancel if not ready!
echo.
pause

echo.
echo [STARTING] Autonomous loop...
echo Press Ctrl+C to stop at any time!
echo.

cd C:\traktor
.\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'C:\traktor\autonomous_dj'); from vision_guided_workflow import VisionGuidedWorkflow; print('\n=== VISION WORKFLOW - AUTONOMOUS LOOP ===\n'); print('Press Ctrl+C to stop\n'); w = VisionGuidedWorkflow(); w.run_loop(max_iterations=None)"

echo.
echo ============================================================
echo Workflow stopped.
echo ============================================================
echo.
pause
