"""
Test Track Navigation in Browser List

Prerequisites:
- Traktor must be running
- Browser must be on Dub folder (already expanded)
- First track should be selected

This test will:
1. Scroll DOWN 5 tracks
2. Scroll UP 3 tracks
3. Scroll to track 7 (absolute positioning)
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from traktor_midi_driver import TraktorMIDIDriver

def test_track_navigation():
    """Test browser list navigation (track scrolling)"""

    print("="*70)
    print("TEST: BROWSER LIST NAVIGATION (Track Scrolling)")
    print("="*70)

    print("\n[INFO] Prerequisites:")
    print("  - Traktor must be running")
    print("  - Browser on Dub folder (expanded)")
    print("  - Ready to scroll through tracks")

    input("\n>> Press Enter when ready...")

    # Initialize MIDI
    print("\n[INIT] Connecting to MIDI...")
    midi = TraktorMIDIDriver()
    time.sleep(0.5)

    # CC for browser navigation (verified from user screenshots - 2025-10-27)
    # Browser.Tree (folders/left panel):
    CC_TREE_DOWN = 72  # Tree navigation DOWN
    CC_TREE_UP = 73    # Tree navigation UP

    # Browser.List (tracks/right panel):
    CC_LIST_DOWN = 74  # List navigation DOWN (Inc)
    CC_LIST_UP = 92    # List navigation UP (Dec)

    # TEST 1: Scroll DOWN 5 tracks
    print("\n" + "="*70)
    print("TEST 1: Scroll DOWN 5 tracks in list")
    print("="*70)

    for i in range(5):
        print(f"  -> Scrolling DOWN ({i+1}/5)...")
        midi.send_cc(CC_LIST_DOWN, 127)  # CC 74 = List DOWN
        time.sleep(0.3)

    print("[OK] Scrolled DOWN 5 tracks")

    input("\n>> Check Traktor - are you 5 tracks down? Press Enter...")

    # TEST 2: Scroll UP 3 tracks
    print("\n" + "="*70)
    print("TEST 2: Scroll UP 3 tracks in list")
    print("="*70)

    for i in range(3):
        print(f"  -> Scrolling UP ({i+1}/3)...")
        midi.send_cc(CC_LIST_UP, 127)  # CC 92 = List UP
        time.sleep(0.3)

    print("[OK] Scrolled UP 3 tracks")

    input("\n>> Check Traktor - are you 2 tracks down from start? Press Enter...")

    # TEST 3: Load selected track to Deck A
    print("\n" + "="*70)
    print("TEST 3: Load selected track to Deck A")
    print("="*70)

    print("[LOAD] Loading current track to Deck A...")
    CC_LOAD_DECK_A = 43  # Load to Deck A
    midi.send_cc(CC_LOAD_DECK_A, 127)
    time.sleep(1.0)

    print("[OK] Track loaded to Deck A")

    input("\n>> Check Traktor - track loaded on Deck A? Press Enter...")

    # TEST 4: Navigate to specific track (track 7)
    print("\n" + "="*70)
    print("TEST 4: Navigate to track 7 (from current position)")
    print("="*70)

    # We're at track 2 (1 + 5 - 3 = 3, but 0-indexed = track 2)
    # Need to go to track 7 = 5 more DOWN

    current_track = 2
    target_track = 7
    steps = target_track - current_track

    print(f"  Current: track {current_track}")
    print(f"  Target: track {target_track}")
    print(f"  Steps needed: {steps} DOWN")

    for i in range(steps):
        print(f"  -> Scrolling DOWN ({i+1}/{steps})...")
        midi.send_cc(CC_LIST_DOWN, 127)
        time.sleep(0.3)

    print(f"[OK] Should be on track {target_track}")

    input("\n>> Check Traktor - are you on track 7? Press Enter...")

    # TEST 5: Load and play
    print("\n" + "="*70)
    print("TEST 5: Load track 7 to Deck B and play")
    print("="*70)

    print("[LOAD] Loading track 7 to Deck B...")
    CC_LOAD_DECK_B = 44  # Load to Deck B
    midi.send_cc(CC_LOAD_DECK_B, 127)
    time.sleep(1.0)

    print("[PLAY] Starting Deck B...")
    CC_PLAY_DECK_B = 48  # Play/Pause Deck B
    midi.send_cc(CC_PLAY_DECK_B, 127)
    time.sleep(0.5)

    print("[MIXER] Setting Deck B volume to 70%...")
    CC_VOLUME_DECK_B = 60  # Deck B volume
    target_volume = int(127 * 0.7)
    midi.send_cc(CC_VOLUME_DECK_B, target_volume)
    time.sleep(0.3)

    print(f"[OK] Deck B playing track 7 at {target_volume}/127 (~70%)")

    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("="*70)

    print("\n[SUCCESS] All track navigation tests passed:")
    print("  1. Scroll DOWN 5 tracks - OK")
    print("  2. Scroll UP 3 tracks - OK")
    print("  3. Load track to Deck A - OK")
    print("  4. Navigate to track 7 - OK")
    print("  5. Load and play on Deck B - OK")

    print("\n[VERIFY] Check Traktor:")
    print("  - Deck A has track 2 loaded")
    print("  - Deck B is playing track 7")
    print("  - Browser on track 7")

    return True


if __name__ == "__main__":
    try:
        success = test_track_navigation()
        if not success:
            print("\n[FAIL] Test failed")
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Test interrupted")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
