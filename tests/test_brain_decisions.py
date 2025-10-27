"""
Test suite for Autonomous DJ Brain
Tests intelligent decision making for track selection.

NOTE: These tests may require OpenRouter API key for full functionality.
Fallback mode will be used if API key not configured.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_dj.autonomous_dj_brain import AutonomousDJBrain


def test_decide_next_track_basic():
    """Test: Decide next track with basic state"""
    print("\n🧪 TEST 1: Decide Next Track (Basic State)")
    print("=" * 50)

    brain = AutonomousDJBrain()

    current_state = {
        "playing_deck": "A",
        "current_track": {"bpm": 128, "key": "8A", "genre": "Techno"},
        "energy_level": "medium",
        "genre_preference": "Techno",
        "tracks_played": 2,
        "session_duration_minutes": 10
    }

    decision = brain.decide_next_track(current_state)

    print(f"Decision: {decision}")
    print(f"Folder: {decision['folder_name']}")
    print(f"BPM range: {decision['track_criteria']['bpm_min']}-{decision['track_criteria']['bpm_max']}")
    print(f"Compatible keys: {decision['track_criteria']['compatible_keys']}")
    print(f"Reasoning: {decision['reasoning']}")

    # Validate decision
    assert decision['folder_name'] in ["Techno", "Dub", "House"], f"Unexpected folder: {decision['folder_name']}"
    assert 110 <= decision['track_criteria']['bpm_min'] <= 145, "BPM range should be reasonable"
    print("✅ TEST PASSED")
    return True


def test_should_load_next_track():
    """Test: Timing decision for loading next track"""
    print("\n🧪 TEST 2: Should Load Next Track Decision")
    print("=" * 50)

    brain = AutonomousDJBrain()

    # Case 1: Many bars remaining
    state1 = {"bars_remaining": 64, "is_playing": True}
    should_load1 = brain.should_load_next_track(state1)
    print(f"Case 1 (64 bars): {should_load1} (expected: False)")
    assert not should_load1, "Should NOT load with 64 bars remaining"

    # Case 2: Few bars remaining
    state2 = {"bars_remaining": 24, "is_playing": True}
    should_load2 = brain.should_load_next_track(state2)
    print(f"Case 2 (24 bars): {should_load2} (expected: True)")
    assert should_load2, "SHOULD load with 24 bars remaining"

    # Case 3: Not playing
    state3 = {"bars_remaining": 20, "is_playing": False}
    should_load3 = brain.should_load_next_track(state3)
    print(f"Case 3 (not playing): {should_load3} (expected: False)")
    assert not should_load3, "Should NOT load if not playing"

    print("✅ TEST PASSED")
    return True


def test_mix_strategy():
    """Test: Mix strategy decision"""
    print("\n🧪 TEST 3: Mix Strategy Decision")
    print("=" * 50)

    brain = AutonomousDJBrain()

    deck_a = {"bpm": 128, "key": "8A", "is_playing": True, "bars_remaining": 16}
    deck_b = {"bpm": 130, "key": "8B", "is_playing": False}

    strategy = brain.decide_mix_strategy(deck_a, deck_b)

    print(f"Strategy: {strategy}")
    print(f"Duration: {strategy['crossfader_duration_seconds']}s")
    print(f"Start at: {strategy['start_at_bars_remaining']} bars remaining")
    print(f"EQ strategy: {strategy['eq_strategy']}")

    assert strategy['crossfader_duration_seconds'] > 0, "Duration must be positive"
    assert strategy['crossfader_duration_seconds'] == 8, "Expected 8 second default duration"
    print("✅ TEST PASSED")
    return True


def run_all_tests():
    """Run all brain tests"""
    print("\n" + "=" * 70)
    print("🧠 AUTONOMOUS DJ BRAIN TEST SUITE")
    print("=" * 70)

    tests = [
        test_decide_next_track_basic,
        test_should_load_next_track,
        test_mix_strategy
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"❌ TEST ERROR: {test_func.__name__} - {e}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")
    return passed == total


if __name__ == "__main__":
    run_all_tests()
