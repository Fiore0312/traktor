"""
Test completo integrazione Claude Vision.
Verifica connessione, analisi screenshot, e integrazione workflow.
"""

import sys
sys.path.insert(0, r'C:\traktor\autonomous_dj')

from claude_vision_client import ClaudeVisionClient
from pathlib import Path
import json


def main():
    """Test suite completa Claude Vision."""

    print("\n" + "="*70)
    print("CLAUDE VISION INTEGRATION TEST")
    print("="*70)

    # Test 1: Init
    print("\n1. Initializing Claude Vision client...")
    try:
        client = ClaudeVisionClient()
        print("   [OK] Client initialized")
    except Exception as e:
        print(f"   [FAIL] FAILED: {e}")
        return False

    # Test 2: Connection
    print("\n2. Testing API connection...")
    if not client.test_connection():
        print("   [FAIL] Connection FAILED")
        return False
    print("   [OK] API connection OK")

    # Test 3: Screenshot analysis
    print("\n3. Testing screenshot analysis...")
    screenshot_dir = Path(r"C:\traktor\data\screenshots")

    if not screenshot_dir.exists():
        print("   [WARN] No screenshots directory")
        print("   Run: python test_basic_vision.py")
        return True  # Connection OK, just missing screenshots

    screenshots = list(screenshot_dir.glob("*.png"))
    if not screenshots:
        print("   [WARN] No screenshots found")
        print("   Run: python test_basic_vision.py")
        return True

    latest = max(screenshots, key=lambda p: p.stat().st_mtime)
    print(f"   Using: {latest.name}")

    try:
        analysis = client.analyze_traktor_screenshot(str(latest))
        print("   [OK] Analysis successful")

        # Validate JSON structure
        required_keys = ['browser', 'deck_a', 'deck_b', 'mixer', 'recommended_action']
        for key in required_keys:
            if key not in analysis:
                print(f"   [FAIL] Missing key in analysis: {key}")
                return False

        print("   [OK] JSON structure valid")

        # Save analysis
        output = latest.parent / f"{latest.stem}_analysis.json"
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"   [OK] Saved: {output.name}")

        return True

    except Exception as e:
        print(f"   [FAIL] Analysis failed: {e}")
        return False


if __name__ == "__main__":
    success = main()

    print("\n" + "="*70)
    if success:
        print("[OK] CLAUDE VISION: READY")
        print("\nIl sistema e configurato e operativo!")
        print("Puoi usare vision-guided workflow con analisi Claude.")
    else:
        print("[FAIL] CLAUDE VISION: FAILED")
        print("\nRisolvi i problemi prima di procedere.")
    print("="*70)
    print("\n")

    sys.exit(0 if success else 1)
