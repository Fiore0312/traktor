"""
Test rapido del Vision-Guided Workflow.
Verifica tutti i componenti integrati prima del loop completo.
"""

import sys
sys.path.insert(0, r'C:\traktor\autonomous_dj')

from vision_guided_workflow import VisionGuidedWorkflow
import time


def test_components():
    """Test individuali di ogni componente."""

    print("\n" + "="*70)
    print("VISION WORKFLOW COMPONENT TEST")
    print("="*70)

    # Test 1: Initialization
    print("\n1. Testing component initialization...")
    try:
        workflow = VisionGuidedWorkflow()
        print("   [OK] All components initialized")
    except Exception as e:
        print(f"   [FAIL] Initialization failed: {e}")
        return False

    # Test 2: Screenshot capture
    print("\n2. Testing screenshot capture...")
    try:
        screenshot = workflow.capture_traktor_screenshot()
        print(f"   [OK] Screenshot captured: {screenshot}")
    except Exception as e:
        print(f"   [FAIL] Screenshot capture failed: {e}")
        return False

    # Test 3: Claude Vision analysis
    print("\n3. Testing Claude Vision analysis...")
    try:
        analysis = workflow.analyze_ui(screenshot)
        print(f"   [OK] Analysis completed")
        print(f"   Browser: {analysis['browser']['track_highlighted']}")
        print(f"   Deck A: {analysis['deck_a']['status']}")
        print(f"   Deck B: {analysis['deck_b']['status']}")
        print(f"   Action: {analysis['recommended_action']['action']}")
    except Exception as e:
        print(f"   [FAIL] Analysis failed: {e}")
        return False

    # Test 4: Action execution (DRY RUN - no actual execution)
    print("\n4. Testing action logic...")
    try:
        action = analysis['recommended_action']['action']
        print(f"   [OK] Would execute: {action}")
        print(f"   Reasoning: {analysis['recommended_action']['reasoning']}")
        print(f"   Safety: {analysis['recommended_action']['safety_check']}")
    except Exception as e:
        print(f"   [FAIL] Action logic failed: {e}")
        return False

    # Cleanup
    workflow.cleanup()

    print("\n" + "="*70)
    print("[OK] ALL COMPONENT TESTS PASSED")
    print("="*70)
    print("\nWorkflow is ready for full loop execution!")
    print("\n")

    return True


def test_single_iteration():
    """Test una singola iterazione completa del workflow."""

    print("\n" + "="*70)
    print("SINGLE ITERATION TEST")
    print("="*70)
    print("\nQuesto test esegue UNA iterazione completa:")
    print("  - Capture screenshot")
    print("  - Analyze con Claude")
    print("  - Execute action (CON MIDI REALE)")
    print()

    confirm = input("Confermi esecuzione? Traktor deve essere aperto! (y/n): ")

    if confirm.lower() != 'y':
        print("\n[CANCELLED] Test cancelled by user")
        return False

    print("\n[START] Starting single iteration test...")

    try:
        workflow = VisionGuidedWorkflow()
        workflow.run_loop(max_iterations=1)

        print("\n" + "="*70)
        print("[OK] SINGLE ITERATION COMPLETED")
        print("="*70)
        print(f"\nAction executed: {workflow.last_action}")
        print("\nVerifica Traktor per confermare che l'azione sia stata eseguita!")
        print("\n")

        return True

    except Exception as e:
        print(f"\n[FAIL] Iteration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Menu test."""

    print("\n")
    print("="*70)
    print("VISION WORKFLOW TEST SUITE")
    print("="*70)
    print()
    print("TEST DISPONIBILI:")
    print("  1. Component test (no MIDI, solo verifica setup)")
    print("  2. Single iteration test (con MIDI, azione reale)")
    print("  3. Full workflow (vai direttamente a vision_guided_workflow.py)")
    print()

    choice = input("Scegli test (1-3): ").strip()

    if choice == "1":
        print("\n[MODE] Component test - safe mode")
        success = test_components()
    elif choice == "2":
        print("\n[MODE] Single iteration - LIVE mode")
        success = test_single_iteration()
    elif choice == "3":
        print("\n[MODE] Full workflow")
        print("Esegui invece: python vision_guided_workflow.py")
        return
    else:
        print("\n[ERROR] Scelta non valida")
        return

    if success:
        print("\n[SUCCESS] Test completato con successo!")
    else:
        print("\n[FAIL] Test fallito")


if __name__ == "__main__":
    main()
