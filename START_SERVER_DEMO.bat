@echo off
REM ============================================================================
REM DJ AI - Start Demo Server
REM ============================================================================

echo ======================================================================
echo DJ AI - Starting Demo Server
echo ======================================================================
echo.
echo Frontend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ======================================================================
echo.

cd /d C:\traktor
.\venv\Scripts\python.exe -m uvicorn server_demo:app --host 127.0.0.1 --port 8000 --reload

pause
