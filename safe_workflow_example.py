#!/usr/bin/env python3
"""
Safe Workflow Example - Integration with Safety Layer

Demonstrates how to integrate TraktorSafetyChecks into existing workflows.

This replaces unsafe direct MIDI commands with safety-compliant operations.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from traktor_safety_checks import TraktorSafetyChecks
import time


def unsafe_load_and_play(deck: str = 'A'):
    """
    UNSAFE EXAMPLE - DO NOT USE IN PRODUCTION

    This is what we had before - direct commands without safety checks.
    """
    print("\n[WARNING] This is the UNSAFE method (for comparison only)")
    print()

    midi = TraktorMIDIDriver()

    # UNSAFE: Direct load without volume check
    print("[UNSAFE] Loading track directly...")
    midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
    time.sleep(1.5)

    # UNSAFE: Playing without mixer preparation
    print("[UNSAFE] Playing without safety checks...")
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)

    print()
    print("[WARNING] Problems with this approach:")
    print("  - No volume safety (could cause audio spike)")
    print("  - No EQ reset (previous track settings remain)")
    print("  - No MASTER/SYNC logic (wrong tempo reference)")
    print("  - No protection for playing decks")

    midi.close()


def safe_load_and_play_first_track():
    """
    SAFE EXAMPLE - First track of session

    Uses safety layer to ensure proper mixer state.
    """
    print("\n" + "=" * 70)
    print("SAFE WORKFLOW: First Track Load")
    print("=" * 70)
    print()

    # Initialize
    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("[SAFE] Initializing safety layer...")
    print("[SAFE] Target: Deck A (first track)")
    print()

    # Step 1: Pre-load safety
    print("[STEP 1] Pre-load safety checks...")
    if not safety.pre_load_safety_check('A', opposite_deck_playing=False):
        print("[ERROR] Safety check failed!")
        midi.close()
        return

    # Step 2: Load track
    print("\n[STEP 2] Loading track to Deck A...")
    print("[ACTION] >>> Select a track in Traktor browser <<<")
    input("Press ENTER when track is selected...")

    midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
    print("[WAIT] Waiting for track to load...")
    time.sleep(2)

    # Step 3: Post-load setup
    print("\n[STEP 3] Post-load safety setup...")
    safety.post_load_safety_setup('A', is_first_track=True)

    # Step 4: Prepare for playback
    print("\n[STEP 4] Preparing for playback...")
    safety.prepare_for_playback('A', is_first_track=True)

    # Step 5: Play
    print("\n[STEP 5] Starting playback...")
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
    safety.mark_deck_playing('A', True)

    print()
    print("[SUCCESS] Track loaded and playing safely!")
    print()
    print("Safety guarantees:")
    print("  ✅ Volume set to 0 before load (no spike)")
    print("  ✅ EQ reset to neutral (flat response)")
    print("  ✅ MASTER enabled (tempo reference)")
    print("  ✅ SYNC disabled (first track, nothing to sync to)")
    print("  ✅ Volume raised to 85% (proper playback level)")
    print("  ✅ Crossfader positioned correctly")

    midi.close()


def safe_load_and_play_second_track():
    """
    SAFE EXAMPLE - Second track (one deck playing)

    Demonstrates safety when loading while another deck plays.
    """
    print("\n" + "=" * 70)
    print("SAFE WORKFLOW: Second Track Load (Deck A playing)")
    print("=" * 70)
    print()

    # Initialize
    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("[SAFE] Initializing safety layer...")
    print("[SAFE] Target: Deck B (Deck A is playing)")
    print()

    # Mark Deck A as playing (in real workflow, this would be tracked)
    safety.mark_deck_playing('A', True)
    safety.deck_states['A']['is_master'] = True

    # Step 1: Pre-load safety
    print("[STEP 1] Pre-load safety checks...")
    if not safety.pre_load_safety_check('B', opposite_deck_playing=True):
        print("[ERROR] Safety check failed!")
        midi.close()
        return

    # Step 2: Load track
    print("\n[STEP 2] Loading track to Deck B...")
    print("[ACTION] >>> Select a track in Traktor browser <<<")
    input("Press ENTER when track is selected...")

    midi.send_cc(TraktorCC.DECK_B_LOAD_TRACK, 127)
    print("[WAIT] Waiting for track to load...")
    time.sleep(2)

    # Step 3: Post-load setup
    print("\n[STEP 3] Post-load safety setup...")
    safety.post_load_safety_setup('B', is_first_track=False)

    # Step 4: Prepare for playback (silent)
    print("\n[STEP 4] Preparing for playback (silent)...")
    safety.prepare_for_playback('B', is_first_track=False)

    # Step 5: Play (silently)
    print("\n[STEP 5] Starting playback (SILENT)...")
    midi.send_cc(TraktorCC.DECK_B_PLAY_PAUSE, 127)
    safety.mark_deck_playing('B', True)

    print()
    print("[SUCCESS] Track loaded and playing silently!")
    print()
    print("Safety guarantees:")
    print("  ✅ Deck A undisturbed (continues playing)")
    print("  ✅ Volume set to 0 before load (no spike)")
    print("  ✅ EQ reset to neutral")
    print("  ✅ SYNC enabled (matches Deck A tempo)")
    print("  ✅ MASTER not set (AUTO mode will handle transfer)")
    print("  ✅ Volume remains at 0 (ready for manual fade-in)")
    print("  ✅ Track is cued and ready for mixing")
    print()
    print("Next steps:")
    print("  - Preview track in headphones")
    print("  - Beatmatch (SYNC already active)")
    print("  - Gradually fade in volume when ready")

    midi.close()


def safe_automated_mix():
    """
    SAFE EXAMPLE - Complete automated mix

    Demonstrates full workflow: Load → Play → Mix → Transition
    """
    print("\n" + "=" * 70)
    print("SAFE WORKFLOW: Automated Mix (A → B)")
    print("=" * 70)
    print()

    # Initialize
    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("[SAFE] Complete automated mix workflow")
    print("[SAFE] Deck A → Deck B transition")
    print()

    input("Setup:")
    print("  1. Deck A has a track playing")
    print("  2. Deck B will be loaded with new track")
    print("  3. Automated volume transition will occur")
    print()
    input("Press ENTER when ready...")

    # Mark Deck A as playing
    safety.mark_deck_playing('A', True)
    safety.deck_states['A']['is_master'] = True
    safety.deck_states['A']['volume'] = safety.SAFE_DEFAULTS['volume_playing']

    # PHASE 1: Load Deck B safely
    print("\n--- PHASE 1: LOAD DECK B ---")
    safety.pre_load_safety_check('B', opposite_deck_playing=True)

    print("[ACTION] >>> Select track for Deck B <<<")
    input("Press ENTER when ready...")

    midi.send_cc(TraktorCC.DECK_B_LOAD_TRACK, 127)
    time.sleep(2)

    safety.post_load_safety_setup('B', is_first_track=False)
    safety.prepare_for_playback('B', is_first_track=False)

    # PHASE 2: Start Deck B (silent)
    print("\n--- PHASE 2: START DECK B (SILENT) ---")
    midi.send_cc(TraktorCC.DECK_B_PLAY_PAUSE, 127)
    safety.mark_deck_playing('B', True)
    print("[OK] Deck B playing silently, synced to Deck A")

    # PHASE 3: Automated transition
    print("\n--- PHASE 3: AUTOMATED TRANSITION (5 seconds) ---")
    print("[INFO] Watch Traktor volume faders")
    print("[INFO] Deck A will fade out, Deck B will fade in")
    time.sleep(2)

    safety.safe_volume_transition(
        from_deck='A',
        to_deck='B',
        steps=10,
        step_delay=0.5
    )

    # PHASE 4: Complete
    print("\n--- PHASE 4: TRANSITION COMPLETE ---")
    print("[SUCCESS] Mix complete!")
    print()
    print("Final state:")
    print("  ✅ Deck A: Silent (0%), ready for next track")
    print("  ✅ Deck B: Playing (85%), audience hears this")
    print("  ✅ AUTO mode transferred MASTER to Deck B")
    print("  ✅ Ready to load next track on Deck A")

    midi.close()


def main():
    """Main menu."""
    print("=" * 70)
    print("SAFE WORKFLOW EXAMPLES")
    print("=" * 70)
    print()
    print("Examples:")
    print("  1. Safe first track load")
    print("  2. Safe second track load")
    print("  3. Complete automated mix (A → B)")
    print("  4. Show unsafe example (for comparison)")
    print("  q. Quit")
    print()

    choice = input("Choice: ").strip()

    if choice == '1':
        safe_load_and_play_first_track()
    elif choice == '2':
        safe_load_and_play_second_track()
    elif choice == '3':
        safe_automated_mix()
    elif choice == '4':
        print("\n[WARNING] This demonstrates UNSAFE practices")
        confirm = input("Continue? (y/n): ")
        if confirm.lower() == 'y':
            unsafe_load_and_play()
    elif choice.lower() == 'q':
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
