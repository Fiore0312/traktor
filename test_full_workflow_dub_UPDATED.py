"""
Test Complete Workflow: Navigate to Dub and Play (UPDATED VERSION)

Uses the corrected AutonomousBrowserNavigator with proper 5-step hierarchy.

This test does:
1. Set volumes to 0
2. Set crossfader to center
3. Navigate to Dub folder (using AutonomousBrowserNavigator)
4. Load random track on Deck A
5. Start playing
6. Fade in volume

UPDATED: Uses AutonomousBrowserNavigator instead of manual navigation.
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from traktor_midi_driver import TraktorMIDIDriver
from autonomous_dj.generated.autonomous_browser_navigator import AutonomousBrowserNavigator

def test_full_workflow():
    """Complete workflow test using corrected navigator"""

    print("="*70)
    print("TEST: COMPLETE WORKFLOW - Navigate to Dub and Play (UPDATED)")
    print("="*70)
    print("\n[INFO] This test uses the corrected AutonomousBrowserNavigator")
    print("       with proper 5-step hierarchy (no C:\\Users\\Utente\\Music level)")

    # Initialize MIDI
    print("\n[INIT] Connecting to MIDI...")
    midi = TraktorMIDIDriver()

    # Initialize navigator
    print("[INIT] Creating autonomous navigator...")
    navigator = AutonomousBrowserNavigator(midi)

    time.sleep(1)

    # STEP 1: Safety - Set volumes to 0
    print("\n" + "="*70)
    print("STEP 1: SAFETY - Set volumes to 0")
    print("="*70)

    print("[SAFETY] Setting Deck A volume to 0...")
    midi.send_cc(65, 0)  # Deck A volume
    time.sleep(0.3)

    print("[SAFETY] Setting Deck B volume to 0...")
    midi.send_cc(60, 0)  # Deck B volume
    time.sleep(0.3)

    print("[OK] Both decks volume at 0")

    # STEP 2: Set crossfader to center
    print("\n" + "="*70)
    print("STEP 2: Set crossfader to center")
    print("="*70)

    print("[MIXER] Setting crossfader to center (64)...")
    midi.send_cc(56, 64)  # Crossfader center
    time.sleep(0.3)

    print("[OK] Crossfader at center")

    # STEP 3: Navigate to Dub using AutonomousBrowserNavigator
    print("\n" + "="*70)
    print("STEP 3: Navigate to Dub folder (using AutonomousBrowserNavigator)")
    print("="*70)

    success, msg = navigator.navigate_to_folder("Dub")

    if not success:
        print(f"[FAIL] Navigation failed: {msg}")
        return False

    print("[OK] Navigated to Dub folder using AutonomousBrowserNavigator!")

    # STEP 4: Load track on Deck A
    print("\n" + "="*70)
    print("STEP 4: Load track on Deck A")
    print("="*70)

    print("[LOAD] Loading selected track to Deck A...")
    midi.send_cc(43, 127)  # CC 43 = Load to Deck A
    time.sleep(1.5)

    print("[OK] Track loaded on Deck A")

    # STEP 5: Start playing
    print("\n" + "="*70)
    print("STEP 5: Start playing Deck A")
    print("="*70)

    print("[PLAY] Starting Deck A...")
    midi.send_cc(47, 127)  # CC 47 = Play/Pause Deck A
    time.sleep(0.5)

    print("[OK] Deck A playing!")

    # STEP 6: Fade in volume
    print("\n" + "="*70)
    print("STEP 6: Fade in volume")
    print("="*70)

    print("[MIXER] Fading in Deck A volume to 85%...")
    target_volume = int(127 * 0.85)  # 108

    # Gradual fade
    for vol in range(0, target_volume, 10):
        midi.send_cc(65, vol)
        time.sleep(0.1)

    # Final volume
    midi.send_cc(65, target_volume)
    time.sleep(0.3)

    print(f"[OK] Deck A volume at {target_volume}/127 (~85%)")

    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*70)

    print("\n[SUCCESS] Workflow complete:")
    print("  1. Volumes set to 0 - OK")
    print("  2. Crossfader centered - OK")
    print("  3. Navigated to Dub (using AutonomousBrowserNavigator) - OK")
    print("  4. Loaded track on Deck A - OK")
    print("  5. Started playing - OK")
    print("  6. Faded in volume - OK")

    print("\n[PLAYING] Deck A is now playing a track from Dub folder!")
    print("          Volume at 85%, crossfader centered")
    print("\n[VERIFY] Please check Traktor to confirm:")
    print("         - Browser is on Dub folder")
    print("         - Deck A is playing a Dub track")
    print("         - Volume is at ~85%")

    return True


if __name__ == "__main__":
    try:
        success = test_full_workflow()
        if not success:
            print("\n[FAIL] Test failed - check errors above")
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Test interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
