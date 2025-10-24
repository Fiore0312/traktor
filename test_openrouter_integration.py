"""
Test integrazione OpenRouter API.
Verifica connessione, modello, e analisi screenshot base.
"""

import sys
sys.path.insert(0, r'C:\traktor\autonomous_dj')

from ai_client import DJAIAssistant
from pathlib import Path
import json


def test_openrouter():
    """Test completo integrazione OpenRouter."""

    print("="*70)
    print("OPENROUTER INTEGRATION TEST")
    print("="*70)

    # Init client
    print("\n1. Initializing AI client...")
    try:
        ai = DJAIAssistant()
        print("   [OK] Client initialized")
    except Exception as e:
        print(f"   [FAIL] FAILED: {e}")
        return False

    # Test connection
    print("\n2. Testing connection...")
    if not ai.test_connection():
        print("   [FAIL] Connection FAILED")
        print("\n   TROUBLESHOOTING:")
        print("   - Check API key in config.py")
        print("   - Verify internet connection")
        print("   - Check OpenRouter status: https://status.openrouter.ai")
        return False
    print("   [OK] Connection OK")

    # Test screenshot analysis
    print("\n3. Testing screenshot analysis...")
    screenshot_dir = Path(r"C:\traktor\data\screenshots")

    if not screenshot_dir.exists():
        print("   [WARN] Screenshot directory not found")
        print("   Crea uno screenshot prima con: python test_basic_vision.py")
        return True  # Connection OK, solo screenshot mancante

    screenshots = list(screenshot_dir.glob("*.png"))
    if not screenshots:
        print("   [WARN] No screenshots available")
        print("   Crea uno screenshot con: python test_basic_vision.py")
        return True

    # Usa screenshot più recente
    latest = max(screenshots, key=lambda p: p.stat().st_mtime)
    print(f"   Using: {latest.name}")

    try:
        analysis = ai.analyze_traktor_screenshot(str(latest))

        print("\n   [OK] Analysis successful!")
        print("\n   RESULTS:")
        print(f"   Browser folder: {analysis['browser']['folder_name']}")
        print(f"   Track highlighted: {analysis['browser']['track_highlighted']}")
        print(f"   Deck A: {analysis['deck_a']['status']}")
        print(f"   Deck B: {analysis['deck_b']['status']}")
        print(f"   Recommended: {analysis['recommended_action']['action']}")
        print(f"   Reasoning: {analysis['recommended_action']['reasoning']}")

        # Save analysis
        output_file = latest.parent / f"{latest.stem}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"\n   [SAVED] Analysis saved: {output_file}")

        return True

    except Exception as e:
        print(f"   [FAIL] Analysis FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    success = test_openrouter()

    print("\n" + "="*70)
    if success:
        print("[OK] OPENROUTER INTEGRATION: READY")
        print("\nIl sistema AI e configurato e funzionante!")
        print("Puoi ora usare vision-guided workflow con analisi automatica.")
    else:
        print("[FAIL] OPENROUTER INTEGRATION: FAILED")
        print("\nRisolvi i problemi sopra prima di procedere.")
    print("="*70)
    print("\n")
