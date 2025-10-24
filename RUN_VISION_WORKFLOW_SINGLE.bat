@echo off
echo ============================================================
echo VISION WORKFLOW - SINGLE ITERATION (LIVE MODE)
echo ============================================================
echo.
echo WARNING: This will execute REAL MIDI commands to Traktor!
echo.
echo What this does:
echo   1. Capture screenshot of Traktor
echo   2. Analyze with Claude Vision AI
echo   3. Execute recommended action (MIDI control)
echo   4. Verify and stop
echo.
echo REQUIREMENTS:
echo   - Traktor Pro 3 must be OPEN and running
echo   - Audio interface connected
echo   - loopMIDI "Traktor MIDI Bus 1" active
echo.
echo Press Ctrl+C NOW to cancel if not ready!
echo.
pause

echo.
echo [STARTING] Running single iteration...
echo.

cd C:\traktor
.\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'C:\traktor\autonomous_dj'); from vision_guided_workflow import VisionGuidedWorkflow; print('\n=== VISION WORKFLOW - SINGLE ITERATION ===\n'); w = VisionGuidedWorkflow(); w.run_loop(max_iterations=1); print('\n[DONE] Check Traktor to verify action was executed!')"

echo.
echo ============================================================
echo Workflow iteration completed.
echo Check Traktor to see what action was executed!
echo ============================================================
echo.
pause
