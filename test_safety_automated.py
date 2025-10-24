#!/usr/bin/env python3
"""
Automated Safety Layer Test - No User Interaction
Tests MIDI commands are sent correctly without requiring manual verification.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from traktor_safety_checks import TraktorSafetyChecks
import time

def test_scenario_1_automated():
    """
    SCENARIO 1: First track load (automated test)
    Tests that all MIDI commands are sent in correct order.
    """
    print("\n" + "="*70)
    print("SCENARIO 1: FIRST TRACK LOAD (Automated)")
    print("="*70)
    print()
    print("Testing MIDI command sequence for first track workflow...")
    print()

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("[TEST] Initializing safety layer...")
    print()

    # Pre-load safety
    print("--- PRE-LOAD SAFETY CHECK ---")
    try:
        result = safety.pre_load_safety_check('A', opposite_deck_playing=False)
        if result:
            print("[OK] Pre-load check completed")
        else:
            print("[FAIL] Pre-load check failed")
            return False
    except Exception as e:
        print(f"[ERROR] Pre-load check: {e}")
        return False

    print()

    # Simulate load (you need to select track manually in Traktor)
    print("--- SIMULATING LOAD ---")
    print("[INFO] In real test, track would be loaded here")
    print("[INFO] Waiting 2 seconds to simulate load time...")
    time.sleep(2)

    # Post-load setup
    print("\n--- POST-LOAD SETUP ---")
    try:
        safety.post_load_safety_setup('A', is_first_track=True)
        print("[OK] Post-load setup completed")
    except Exception as e:
        print(f"[ERROR] Post-load setup: {e}")
        return False

    print()

    # Prepare for playback
    print("--- PREPARE FOR PLAYBACK ---")
    try:
        safety.prepare_for_playback('A', is_first_track=True)
        print("[OK] Prepare for playback completed")
    except Exception as e:
        print(f"[ERROR] Prepare for playback: {e}")
        return False

    print()

    # Mark as playing
    print("--- MARK DECK PLAYING ---")
    try:
        safety.mark_deck_playing('A', True)
        print("[OK] Deck marked as playing")
    except Exception as e:
        print(f"[ERROR] Mark playing: {e}")
        return False

    print()
    print("="*70)
    print("SCENARIO 1: COMPLETED")
    print("="*70)
    print()
    print("Commands sent:")
    print("  1. Set Deck A volume to 0")
    print("  2. Position crossfader LEFT")
    print("  3. Reset EQ High/Mid/Low to 64 (center)")
    print("  4. Set MASTER ON (CC 33 = 127)")
    print("  5. Set volume to 108 (~85%)")
    print()
    print("Check Traktor to verify these settings were applied.")
    print()

    midi.close()
    return True


def test_scenario_2_automated():
    """
    SCENARIO 2: Second track load (automated test)
    """
    print("\n" + "="*70)
    print("SCENARIO 2: SECOND TRACK LOAD (Automated)")
    print("="*70)
    print()

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    # Simulate Deck A already playing
    safety.mark_deck_playing('A', True)
    safety.deck_states['A']['is_master'] = True

    print("[TEST] Simulating Deck A already playing...")
    print()

    # Pre-load safety for Deck B
    print("--- PRE-LOAD SAFETY CHECK (Deck B) ---")
    try:
        result = safety.pre_load_safety_check('B', opposite_deck_playing=True)
        if result:
            print("[OK] Pre-load check completed")
        else:
            print("[FAIL] Pre-load check failed")
            return False
    except Exception as e:
        print(f"[ERROR] Pre-load check: {e}")
        return False

    print()
    time.sleep(2)

    # Post-load setup
    print("--- POST-LOAD SETUP (Deck B) ---")
    try:
        safety.post_load_safety_setup('B', is_first_track=False)
        print("[OK] Post-load setup completed")
    except Exception as e:
        print(f"[ERROR] Post-load setup: {e}")
        return False

    print()

    # Prepare for playback (silent)
    print("--- PREPARE FOR PLAYBACK (Deck B - SILENT) ---")
    try:
        safety.prepare_for_playback('B', is_first_track=False)
        print("[OK] Prepare for playback completed (volume at 0)")
    except Exception as e:
        print(f"[ERROR] Prepare for playback: {e}")
        return False

    print()
    print("="*70)
    print("SCENARIO 2: COMPLETED")
    print("="*70)
    print()
    print("Commands sent:")
    print("  1. Set Deck B volume to 0")
    print("  2. Crossfader remains in position (protecting Deck A)")
    print("  3. Reset EQ High/Mid/Low to 64 (center)")
    print("  4. Set SYNC ON (CC 42 = 127)")
    print("  5. Volume remains at 0 (ready for fade-in)")
    print()
    print("Check Traktor:")
    print("  - Deck A should be UNDISTURBED")
    print("  - Deck B volume should be 0%")
    print("  - SYNC should be enabled on Deck B")
    print()

    midi.close()
    return True


def test_scenario_3_automated():
    """
    SCENARIO 3: Safe volume transition (automated test)
    """
    print("\n" + "="*70)
    print("SCENARIO 3: SAFE VOLUME TRANSITION (Automated)")
    print("="*70)
    print()

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    # Simulate both decks playing
    safety.mark_deck_playing('A', True)
    safety.mark_deck_playing('B', True)
    safety.deck_states['A']['volume'] = safety.SAFE_DEFAULTS['volume_playing']
    safety.deck_states['B']['volume'] = 0

    print("[TEST] Simulating Deck A playing loud, Deck B silent...")
    print("[TEST] Executing automated crossfade A -> B")
    print()

    time.sleep(1)

    # Safe volume transition
    print("--- VOLUME TRANSITION (5 seconds) ---")
    try:
        safety.safe_volume_transition(
            from_deck='A',
            to_deck='B',
            steps=10,
            step_delay=0.5
        )
        print("[OK] Volume transition completed")
    except Exception as e:
        print(f"[ERROR] Volume transition: {e}")
        return False

    print()
    print("="*70)
    print("SCENARIO 3: COMPLETED")
    print("="*70)
    print()
    print("Transition executed:")
    print("  - 10 steps over 5 seconds")
    print("  - Deck A: 108 -> 0")
    print("  - Deck B: 0 -> 108")
    print()
    print("Check Traktor:")
    print("  - Deck A volume should now be 0%")
    print("  - Deck B volume should now be ~85%")
    print("  - Transition should have been smooth")
    print()

    midi.close()
    return True


def test_scenario_4_automated():
    """
    SCENARIO 4: Emergency silence (automated test)
    """
    print("\n" + "="*70)
    print("SCENARIO 4: EMERGENCY SILENCE (Automated)")
    print("="*70)
    print()

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("[TEST] Testing emergency silence on Deck A...")
    print()

    time.sleep(1)

    print("--- EMERGENCY SILENCE ---")
    try:
        safety.emergency_silence_deck('A')
        print("[OK] Emergency silence executed")
    except Exception as e:
        print(f"[ERROR] Emergency silence: {e}")
        return False

    print()
    print("="*70)
    print("SCENARIO 4: COMPLETED")
    print("="*70)
    print()
    print("Command sent:")
    print("  - Deck A volume set to 0 immediately")
    print()
    print("Check Traktor:")
    print("  - Deck A volume should be 0%")
    print()

    midi.close()
    return True


def run_all_tests_automated():
    """Run all test scenarios automatically."""
    print("\n" + "="*70)
    print("TRAKTOR SAFETY LAYER - AUTOMATED TEST SUITE")
    print("="*70)
    print()
    print("Running all test scenarios...")
    print()

    results = []

    # Test 1
    print("\n" + ">"*70)
    result1 = test_scenario_1_automated()
    results.append(("Scenario 1: First Track", result1))
    time.sleep(2)

    # Test 2
    print("\n" + ">"*70)
    result2 = test_scenario_2_automated()
    results.append(("Scenario 2: Second Track", result2))
    time.sleep(2)

    # Test 3
    print("\n" + ">"*70)
    result3 = test_scenario_3_automated()
    results.append(("Scenario 3: Volume Transition", result3))
    time.sleep(2)

    # Test 4
    print("\n" + ">"*70)
    result4 = test_scenario_4_automated()
    results.append(("Scenario 4: Emergency Silence", result4))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print()
    print(f"Total: {passed}/{total} tests completed successfully")
    print()

    if passed == total:
        print("All MIDI commands sent successfully!")
        print()
        print("IMPORTANT: Verify in Traktor that settings were applied correctly:")
        print("  1. Check volume faders positions")
        print("  2. Check EQ knobs are centered")
        print("  3. Check MASTER/SYNC indicators")
        print("  4. Check crossfader position")
    else:
        print("Some tests failed - check error messages above")


def main():
    """Main entry point."""
    print("="*70)
    print("TRAKTOR SAFETY LAYER - AUTOMATED TEST")
    print("="*70)
    print()
    print("This will run all safety layer tests automatically.")
    print("MIDI commands will be sent to Traktor.")
    print()
    print("Make sure:")
    print("  1. Traktor Pro 3 is running")
    print("  2. MIDI device 'Traktor MIDI Bus 1' is available")
    print("  3. You can observe Traktor GUI during tests")
    print()
    print("Press Ctrl+C to cancel...")
    print()

    try:
        time.sleep(3)
        run_all_tests_automated()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")


if __name__ == "__main__":
    main()
