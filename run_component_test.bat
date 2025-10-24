@echo off
echo ============================================================
echo VISION WORKFLOW - COMPONENT TEST
echo ============================================================
echo.
echo Running component test (safe mode - no MIDI execution)...
echo.

cd C:\traktor
.\venv\Scripts\python.exe -c "import sys; sys.path.insert(0, r'C:\traktor\autonomous_dj'); from vision_guided_workflow import VisionGuidedWorkflow; from pathlib import Path; print('\n=== COMPONENT TEST ===\n'); print('1. Initializing...'); w = VisionGuidedWorkflow(); print('   [OK] Components initialized\n'); print('2. Capturing screenshot...'); s = w.capture_traktor_screenshot(); print(f'   [OK] Screenshot: {Path(s).name}\n'); print('3. Analyzing with Claude Vision...'); a = w.analyze_ui(s); print(f'   [OK] Analysis complete\n'); print('RESULTS:'); print(f'  Browser: {a[\"browser\"][\"track_highlighted\"]}'); print(f'  Deck A: {a[\"deck_a\"][\"status\"]}'); print(f'  Deck B: {a[\"deck_b\"][\"status\"]}'); print(f'  Action: {a[\"recommended_action\"][\"action\"]}'); print(f'  Reasoning: {a[\"recommended_action\"][\"reasoning\"][:80]}...'); print(f'\n[SUCCESS] Component test completed!\n'); w.cleanup()"

echo.
echo ============================================================
echo Test completed. Check output above.
echo ============================================================
pause
