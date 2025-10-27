@echo off
echo ================================================================
echo TRAKTOR LIBRARY MAPPING TRAINING SYSTEM
echo ================================================================
echo.
echo This is the SACRED GRAIL of the navigation system.
echo.
echo What this does:
echo - Maps every folder position in your Traktor browser
echo - Creates navigation_map.json (PRIMARY storage)
echo - Creates navigation_map.db (BACKUP storage)
echo - Auto-saves every 5 folders
echo - Can be interrupted and resumed anytime
echo.
echo IMPORTANT:
echo - Traktor Pro 3 must be RUNNING
echo - You will confirm each folder name
echo - Process can take 30-60 minutes for full library
echo - You can stop anytime (Ctrl+C) and resume later
echo.
pause

.\venv\Scripts\python.exe training_library_mapper.py

echo.
echo ================================================================
echo Training session complete!
echo Check: data/navigation_map.json
echo ================================================================
pause
