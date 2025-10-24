#!/usr/bin/env python3
"""
Test Traktor Safety Layer - Professional DJ Workflow Compliance

Tests the safety checks module with real Traktor instance.

Test Scenarios:
1. First track load (empty session)
2. Second track load (one deck playing)
3. Safe volume transition between decks
4. Emergency silence

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from traktor_safety_checks import TraktorSafetyChecks, safe_load_and_play_workflow
import time


def test_scenario_1_first_track():
    """
    SCENARIO 1: Loading first track of session (empty decks)

    Expected:
    - Volume set to 0 before load
    - EQ reset to neutral after load
    - MASTER enabled
    - SYNC disabled
    - Volume raised to 85% before play
    """
    print("\n" + "=" * 70)
    print("SCENARIO 1: FIRST TRACK LOAD (Empty Session)")
    print("=" * 70)
    print()
    print("Setup:")
    print("  - All decks empty")
    print("  - No audio playing")
    print("  - This will be the MASTER track")
    print()

    input("Make sure:")
    print("  1. Traktor is open")
    print("  2. All decks are empty")
    print("  3. Select a track in browser")
    print()
    input("Press ENTER when ready...")

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("\n[TEST] Executing first track workflow...")

    # Pre-load safety
    print("\n--- PRE-LOAD SAFETY CHECK ---")
    if not safety.pre_load_safety_check('A', opposite_deck_playing=False):
        print("[FAIL] Pre-load check failed!")
        midi.close()
        return False

    # Load track
    print("\n--- LOADING TRACK ---")
    print("[ACTION] Sending LOAD command to Deck A...")
    midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
    print("[WAIT] Waiting 2 seconds for track to load...")
    time.sleep(2)

    # Post-load setup
    print("\n--- POST-LOAD SETUP ---")
    safety.post_load_safety_setup('A', is_first_track=True)

    # Prepare for playback
    print("\n--- PREPARE FOR PLAYBACK ---")
    safety.prepare_for_playback('A', is_first_track=True)

    # Play
    print("\n--- STARTING PLAYBACK ---")
    print("[ACTION] Sending PLAY command to Deck A...")
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
    safety.mark_deck_playing('A', True)

    print("\n" + "=" * 70)
    print("VERIFICATION CHECKLIST")
    print("=" * 70)
    print("Check in Traktor:")
    print("  [ ] Deck A has track loaded")
    print("  [ ] Deck A is PLAYING")
    print("  [ ] Volume fader is at ~85%")
    print("  [ ] EQ knobs are centered (12 o'clock)")
    print("  [ ] MASTER is enabled on Deck A")
    print("  [ ] SYNC is disabled on Deck A")
    print("  [ ] Crossfader is to the LEFT")
    print()

    result = input("All items checked? (y/n): ")

    midi.close()

    if result.lower() == 'y':
        print("\n[PASS] Scenario 1: PASSED")
        return True
    else:
        print("\n[FAIL] Scenario 1: FAILED - Check mixer settings")
        return False


def test_scenario_2_second_track():
    """
    SCENARIO 2: Loading second track (one deck playing)

    Expected:
    - Volume set to 0 before load
    - EQ reset to neutral after load
    - SYNC enabled
    - MASTER NOT enabled (AUTO mode)
    - Volume stays at 0 (ready for manual fade-in)
    """
    print("\n" + "=" * 70)
    print("SCENARIO 2: SECOND TRACK LOAD (One Deck Playing)")
    print("=" * 70)
    print()
    print("Setup:")
    print("  - Deck A is playing (from Scenario 1 or load manually)")
    print("  - Deck B is empty")
    print("  - We'll load to Deck B")
    print()

    input("Make sure:")
    print("  1. Deck A has a track playing")
    print("  2. Deck B is empty")
    print("  3. Select a track in browser")
    print()
    input("Press ENTER when ready...")

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    # Mark Deck A as playing (simulate state)
    safety.mark_deck_playing('A', True)
    safety.deck_states['A']['is_master'] = True

    print("\n[TEST] Executing second track workflow...")

    # Pre-load safety
    print("\n--- PRE-LOAD SAFETY CHECK ---")
    if not safety.pre_load_safety_check('B', opposite_deck_playing=True):
        print("[FAIL] Pre-load check failed!")
        midi.close()
        return False

    # Load track
    print("\n--- LOADING TRACK ---")
    print("[ACTION] Sending LOAD command to Deck B...")
    midi.send_cc(TraktorCC.DECK_B_LOAD_TRACK, 127)
    print("[WAIT] Waiting 2 seconds for track to load...")
    time.sleep(2)

    # Post-load setup
    print("\n--- POST-LOAD SETUP ---")
    safety.post_load_safety_setup('B', is_first_track=False)

    # Prepare for playback
    print("\n--- PREPARE FOR PLAYBACK ---")
    safety.prepare_for_playback('B', is_first_track=False)

    # Play (silent, cued)
    print("\n--- STARTING PLAYBACK (SILENT) ---")
    print("[ACTION] Sending PLAY command to Deck B...")
    print("[INFO] Deck B will play SILENTLY (volume at 0%)")
    midi.send_cc(TraktorCC.DECK_B_PLAY_PAUSE, 127)
    safety.mark_deck_playing('B', True)

    print("\n" + "=" * 70)
    print("VERIFICATION CHECKLIST")
    print("=" * 70)
    print("Check in Traktor:")
    print("  [ ] Deck A is still PLAYING (undisturbed)")
    print("  [ ] Deck B has track loaded")
    print("  [ ] Deck B is PLAYING (waveform moving)")
    print("  [ ] Deck B volume fader is at 0% (silent)")
    print("  [ ] Deck B EQ knobs are centered (12 o'clock)")
    print("  [ ] SYNC is enabled on Deck B")
    print("  [ ] MASTER is still on Deck A (not B)")
    print("  [ ] You hear ONLY Deck A (not Deck B)")
    print()

    result = input("All items checked? (y/n): ")

    midi.close()

    if result.lower() == 'y':
        print("\n[PASS] Scenario 2: PASSED")
        print("\nNext: You can manually fade in Deck B volume to mix")
        return True
    else:
        print("\n[FAIL] Scenario 2: FAILED - Check mixer settings")
        return False


def test_scenario_3_safe_transition():
    """
    SCENARIO 3: Automated safe volume transition

    Expected:
    - Gradual volume crossfade
    - Deck A: 85% → 0%
    - Deck B: 0% → 85%
    - Smooth transition over 5 seconds
    """
    print("\n" + "=" * 70)
    print("SCENARIO 3: SAFE VOLUME TRANSITION (Automated Crossfade)")
    print("=" * 70)
    print()
    print("Setup:")
    print("  - Deck A is playing at 85%")
    print("  - Deck B is playing at 0% (silent)")
    print("  - We'll fade A → B automatically")
    print()

    input("Make sure:")
    print("  1. Both decks have tracks")
    print("  2. Both decks are PLAYING")
    print("  3. Deck A is audible, Deck B is silent")
    print()
    input("Press ENTER to start automated transition...")

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    # Simulate current state
    safety.mark_deck_playing('A', True)
    safety.mark_deck_playing('B', True)
    safety.deck_states['A']['volume'] = safety.SAFE_DEFAULTS['volume_playing']
    safety.deck_states['B']['volume'] = 0

    print("\n[TEST] Executing automated volume transition...")
    print("[INFO] This will take ~5 seconds")
    print("[INFO] Watch the volume faders in Traktor")
    print()

    time.sleep(2)

    # Safe volume transition
    safety.safe_volume_transition(
        from_deck='A',
        to_deck='B',
        steps=10,
        step_delay=0.5
    )

    print("\n" + "=" * 70)
    print("VERIFICATION CHECKLIST")
    print("=" * 70)
    print("Check in Traktor:")
    print("  [ ] Deck A volume fader is now at 0%")
    print("  [ ] Deck B volume fader is now at ~85%")
    print("  [ ] You hear ONLY Deck B (not Deck A)")
    print("  [ ] Transition was smooth (no jumps/clicks)")
    print()

    result = input("All items checked? (y/n): ")

    midi.close()

    if result.lower() == 'y':
        print("\n[PASS] Scenario 3: PASSED")
        return True
    else:
        print("\n[FAIL] Scenario 3: FAILED")
        return False


def test_scenario_4_emergency_silence():
    """
    SCENARIO 4: Emergency silence

    Tests emergency deck silencing.
    """
    print("\n" + "=" * 70)
    print("SCENARIO 4: EMERGENCY SILENCE")
    print("=" * 70)
    print()
    print("This tests the emergency silence function.")
    print("Deck A will be immediately silenced.")
    print()

    input("Make sure:")
    print("  1. Deck A is playing (audible)")
    print()
    input("Press ENTER to trigger emergency silence...")

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("\n[EMERGENCY] Silencing Deck A immediately...")
    safety.emergency_silence_deck('A')

    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print("Check in Traktor:")
    print("  [ ] Deck A volume fader jumped to 0% immediately")
    print("  [ ] No audio from Deck A")
    print()

    result = input("Deck A silenced? (y/n): ")

    midi.close()

    if result.lower() == 'y':
        print("\n[PASS] Scenario 4: PASSED")
        return True
    else:
        print("\n[FAIL] Scenario 4: FAILED")
        return False


def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "=" * 70)
    print("TRAKTOR SAFETY LAYER - COMPLETE TEST SUITE")
    print("=" * 70)
    print()
    print("This will test all safety scenarios:")
    print("  1. First track load (empty session)")
    print("  2. Second track load (one playing)")
    print("  3. Safe automated transition")
    print("  4. Emergency silence")
    print()

    choice = input("Run all tests? (y/n): ")
    if choice.lower() != 'y':
        print("\nTest cancelled")
        return

    results = []

    # Scenario 1
    results.append(("First Track Load", test_scenario_1_first_track()))

    # Scenario 2
    if results[0][1]:  # Only if scenario 1 passed
        results.append(("Second Track Load", test_scenario_2_second_track()))

    # Scenario 3
    if len(results) == 2 and results[1][1]:  # Only if scenario 2 passed
        results.append(("Safe Transition", test_scenario_3_safe_transition()))

    # Scenario 4
    results.append(("Emergency Silence", test_scenario_4_emergency_silence()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - Safety layer working perfectly!")
    else:
        print("\n⚠️ Some tests failed - Check Traktor configuration")


def main():
    """Main entry point."""
    print("=" * 70)
    print("TRAKTOR SAFETY LAYER TEST")
    print("=" * 70)
    print()
    print("Select test scenario:")
    print("  1. First track load (empty session)")
    print("  2. Second track load (one playing)")
    print("  3. Safe automated transition")
    print("  4. Emergency silence")
    print("  5. Run ALL tests")
    print("  q. Quit")
    print()

    choice = input("Choice: ").strip()

    if choice == '1':
        test_scenario_1_first_track()
    elif choice == '2':
        test_scenario_2_second_track()
    elif choice == '3':
        test_scenario_3_safe_transition()
    elif choice == '4':
        test_scenario_4_emergency_silence()
    elif choice == '5':
        run_all_tests()
    elif choice.lower() == 'q':
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
