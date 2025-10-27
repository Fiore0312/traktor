@echo off
REM ============================================================================
REM DJ AI - Start PRODUCTION Server (with Traktor Integration)
REM ============================================================================

echo ======================================================================
echo DJ AI - Starting PRODUCTION Server
echo ======================================================================
echo.
echo IMPORTANT: Before starting, ensure:
echo   1. Traktor Pro 3 is running
echo   2. loopMIDI "Traktor MIDI Bus 1" is configured
echo   3. ASIO driver enabled (NOT WASAPI)
echo   4. MIDI Interaction Mode = "Direct"
echo   5. API keys configured in autonomous_dj/config.py
echo.
echo Frontend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

cd /d C:\traktor
.\venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload

pause
