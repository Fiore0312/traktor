"""
Test semplice del Vision Workflow senza input interattivo.
"""

import sys
sys.path.insert(0, r'C:\traktor\autonomous_dj')

from vision_guided_workflow import VisionGuidedWorkflow
from pathlib import Path


def main():
    """Test componenti base."""

    print("\n" + "="*70)
    print("VISION WORKFLOW - COMPONENT TEST")
    print("="*70)
    print("\nRunning safe mode test (no MIDI execution)...\n")

    # Test 1: Init
    print("1. Initializing components...")
    try:
        workflow = VisionGuidedWorkflow()
        print("   [OK] All components initialized")
    except Exception as e:
        print(f"   [FAIL] Init failed: {e}")
        return False

    # Test 2: Screenshot
    print("\n2. Capturing screenshot...")
    try:
        screenshot = workflow.capture_traktor_screenshot()
        screenshot_name = Path(screenshot).name
        print(f"   [OK] Screenshot: {screenshot_name}")
    except Exception as e:
        print(f"   [FAIL] Screenshot failed: {e}")
        return False

    # Test 3: Analysis
    print("\n3. Analyzing with Claude Vision...")
    try:
        analysis = workflow.analyze_ui(screenshot)
        print(f"   [OK] Analysis complete")
    except Exception as e:
        print(f"   [FAIL] Analysis failed: {e}")
        return False

    # Results
    print("\n" + "="*70)
    print("ANALYSIS RESULTS")
    print("="*70)
    print(f"\nBrowser:")
    print(f"  Folder: {analysis['browser']['folder_name']}")
    print(f"  Track highlighted: {analysis['browser']['track_highlighted']}")

    print(f"\nDeck A:")
    print(f"  Status: {analysis['deck_a']['status']}")
    if analysis['deck_a']['status'] == 'loaded':
        print(f"  Track: {analysis['deck_a']['track_title']}")
        print(f"  Artist: {analysis['deck_a']['artist']}")
        print(f"  BPM: {analysis['deck_a']['bpm']}")
        print(f"  Playing: {analysis['deck_a']['playing']}")

    print(f"\nDeck B:")
    print(f"  Status: {analysis['deck_b']['status']}")
    if analysis['deck_b']['status'] == 'loaded':
        print(f"  Track: {analysis['deck_b']['track_title']}")
        print(f"  Artist: {analysis['deck_b']['artist']}")
        print(f"  BPM: {analysis['deck_b']['bpm']}")
        print(f"  Playing: {analysis['deck_b']['playing']}")

    print(f"\nMixer:")
    print(f"  Deck A volume: {analysis['mixer']['deck_a_volume']}")
    print(f"  Deck B volume: {analysis['mixer']['deck_b_volume']}")
    print(f"  Crossfader: {analysis['mixer']['crossfader']}")
    if analysis['mixer']['warnings']:
        print(f"  Warnings: {', '.join(analysis['mixer']['warnings'])}")

    print(f"\nRecommended Action:")
    print(f"  Action: {analysis['recommended_action']['action']}")
    print(f"  Priority: {analysis['recommended_action']['priority']}")
    print(f"  Safety: {analysis['recommended_action']['safety_check']}")
    print(f"  Reasoning: {analysis['recommended_action']['reasoning']}")

    # Cleanup
    workflow.cleanup()

    print("\n" + "="*70)
    print("[SUCCESS] Component test completed!")
    print("="*70)
    print("\nAll systems operational. Ready for full workflow.\n")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
