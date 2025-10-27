"""
Test suite for Autonomous Orchestrator

Tests main loop logic, state transitions, and decision flow.

NOTE: These tests use mock objects and don't require Traktor running.
They test the orchestrator's logic, not actual MIDI communication.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_dj.autonomous_orchestrator import AutonomousOrchestrator, DJState


def test_initialization():
    """Test: Orchestrator initialization"""
    print("\n🧪 TEST 1: Initialization")
    print("=" * 50)

    # Create with mocked dependencies
    mock_midi = Mock()
    mock_brain = Mock()
    mock_navigator = Mock()

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator,
        start_genre="Techno",
        energy_level="medium"
    )

    # Validate initialization
    assert orchestrator.state == DJState.IDLE, "Should start in IDLE state"
    assert orchestrator.current_genre == "Techno", "Genre should match"
    assert orchestrator.energy_level == "medium", "Energy should match"
    assert orchestrator.tracks_played == 0, "No tracks played yet"
    assert orchestrator.playing_deck is None, "No deck playing yet"

    print(f"State: {orchestrator.state}")
    print(f"Genre: {orchestrator.current_genre}")
    print(f"Energy: {orchestrator.energy_level}")
    print("✅ TEST PASSED")
    return True


def test_start_session():
    """Test: Starting autonomous session"""
    print("\n🧪 TEST 2: Start Session")
    print("=" * 50)

    # Mock dependencies
    mock_midi = Mock()
    mock_midi.load_selected_track.return_value = True
    mock_midi.play_deck.return_value = True

    mock_brain = Mock()
    mock_brain.decide_next_track.return_value = {
        "folder_name": "Techno",
        "track_criteria": {
            "bpm_min": 128,
            "bpm_max": 132,
            "compatible_keys": ["8A"],
            "preferred_track_number": 1
        },
        "reasoning": "Test track selection"
    }

    mock_navigator = Mock()
    mock_navigator.navigate_and_select_track.return_value = (True, "Success")

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator
    )

    # Start session
    success = orchestrator.start_session()

    # Validate
    assert success, "Session should start successfully"
    assert orchestrator.state == DJState.PLAYING, "Should be in PLAYING state"
    assert orchestrator.playing_deck == "A", "Deck A should be playing"
    assert orchestrator.tracks_played == 1, "First track counted"

    # Verify calls
    mock_brain.decide_next_track.assert_called_once()
    mock_navigator.navigate_and_select_track.assert_called_once_with("Techno", 1)
    mock_midi.load_selected_track.assert_called_once_with("A")
    mock_midi.play_deck.assert_called_once_with("A")

    print(f"State: {orchestrator.state}")
    print(f"Playing deck: {orchestrator.playing_deck}")
    print(f"Tracks played: {orchestrator.tracks_played}")
    print("✅ TEST PASSED")
    return True


def test_state_transition_playing_to_loading():
    """Test: Transition from PLAYING to LOADING when bars trigger"""
    print("\n🧪 TEST 3: PLAYING → LOADING Transition")
    print("=" * 50)

    mock_midi = Mock()
    mock_brain = Mock()
    mock_navigator = Mock()

    # Mock should_load_next_track to return True
    mock_brain.should_load_next_track.return_value = True

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator
    )

    # Manually set to PLAYING state
    orchestrator.state = DJState.PLAYING
    orchestrator.playing_deck = "A"
    orchestrator.deck_states["A"]["is_playing"] = True

    # Mock _estimate_bars_remaining to return low bars
    orchestrator._estimate_bars_remaining = Mock(return_value=20)

    # Handle playing state
    orchestrator._handle_playing_state()

    # Validate transition
    assert orchestrator.state == DJState.LOADING, "Should transition to LOADING"
    assert mock_brain.should_load_next_track.called, "Brain should be consulted"

    print(f"State after transition: {orchestrator.state}")
    print(f"Brain called: {mock_brain.should_load_next_track.called}")
    print("✅ TEST PASSED")
    return True


def test_loading_track():
    """Test: Loading next track on idle deck"""
    print("\n🧪 TEST 4: Load Next Track")
    print("=" * 50)

    mock_midi = Mock()
    mock_midi.load_selected_track.return_value = True

    mock_brain = Mock()
    mock_brain.decide_next_track.return_value = {
        "folder_name": "Dub",
        "track_criteria": {
            "bpm_min": 125,
            "bpm_max": 130,
            "compatible_keys": ["8B"],
            "preferred_track_number": 5
        },
        "reasoning": "Compatible with current track"
    }

    mock_navigator = Mock()
    mock_navigator.navigate_and_select_track.return_value = (True, "Navigated to Dub track 5")

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator
    )

    # Setup state
    orchestrator.state = DJState.LOADING
    orchestrator.playing_deck = "A"
    orchestrator.deck_states["A"] = {
        "is_playing": True,
        "track": "Techno/track_1",
        "bpm": 128,
        "key": "8A"
    }

    # Handle loading
    orchestrator._handle_loading_state()

    # Validate
    assert orchestrator.state == DJState.MIXING, "Should transition to MIXING"
    assert orchestrator.loading_deck == "B", "Should load to Deck B"
    assert mock_navigator.navigate_and_select_track.called_with("Dub", 5)
    assert mock_midi.load_selected_track.called_with("B")
    assert mock_midi.enable_sync.called_with("B", True)

    print(f"State: {orchestrator.state}")
    print(f"Loading deck: {orchestrator.loading_deck}")
    print(f"Deck B state: {orchestrator.deck_states['B']}")
    print("✅ TEST PASSED")
    return True


def test_mix_execution():
    """Test: Mix transition execution"""
    print("\n🧪 TEST 5: Mix Execution")
    print("=" * 50)

    mock_midi = Mock()
    mock_brain = Mock()
    mock_brain.decide_mix_strategy.return_value = {
        "crossfader_duration_seconds": 8,
        "start_at_bars_remaining": 16,
        "eq_strategy": "gradual_bass_swap",
        "use_effects": False
    }

    mock_navigator = Mock()

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator
    )

    # Setup state
    orchestrator.state = DJState.MIXING
    orchestrator.playing_deck = "A"
    orchestrator.loading_deck = "B"
    orchestrator.deck_states = {
        "A": {"is_playing": True, "track": "Techno/1", "bpm": 128, "key": "8A"},
        "B": {"is_playing": False, "track": "Dub/5", "bpm": 126, "key": "8B"}
    }
    orchestrator.tracks_played = 1

    # Mock bars remaining to be ready for mix
    orchestrator._estimate_bars_remaining = Mock(return_value=16)

    # Handle mixing (with time acceleration for testing)
    with patch('time.sleep'):  # Skip actual sleep delays
        orchestrator._handle_mixing_state()

    # Validate
    assert orchestrator.state == DJState.PLAYING, "Should return to PLAYING"
    assert orchestrator.playing_deck == "B", "Deck B should now be playing"
    assert orchestrator.loading_deck is None, "No deck loading"
    assert orchestrator.tracks_played == 2, "Track count incremented"
    assert mock_midi.play_deck.called_with("B"), "Deck B should be started"
    assert mock_midi.pause_deck.called_with("A"), "Deck A should be stopped"
    assert mock_midi.set_crossfader.called, "Crossfader should be moved"

    print(f"Final state: {orchestrator.state}")
    print(f"Playing deck: {orchestrator.playing_deck}")
    print(f"Tracks played: {orchestrator.tracks_played}")
    print(f"Crossfader calls: {mock_midi.set_crossfader.call_count}")
    print("✅ TEST PASSED")
    return True


def test_error_handling():
    """Test: Error handling during navigation failure"""
    print("\n🧪 TEST 6: Error Handling")
    print("=" * 50)

    mock_midi = Mock()
    mock_brain = Mock()
    mock_brain.decide_next_track.return_value = {
        "folder_name": "InvalidFolder",
        "track_criteria": {"preferred_track_number": 99},
        "reasoning": "Test"
    }

    mock_navigator = Mock()
    # Simulate navigation failure
    mock_navigator.navigate_and_select_track.return_value = (False, "Folder not found")

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator
    )

    # Setup loading state
    orchestrator.state = DJState.LOADING
    orchestrator.playing_deck = "A"

    # Handle loading (should fail)
    orchestrator._handle_loading_state()

    # Validate error handling
    assert orchestrator.state == DJState.ERROR, "Should transition to ERROR state"

    print(f"State after error: {orchestrator.state}")
    print("✅ TEST PASSED - Error handled correctly")
    return True


def test_cleanup():
    """Test: Cleanup and shutdown"""
    print("\n🧪 TEST 7: Cleanup")
    print("=" * 50)

    mock_midi = Mock()
    mock_brain = Mock()
    mock_navigator = Mock()

    orchestrator = AutonomousOrchestrator(
        midi_driver=mock_midi,
        brain=mock_brain,
        navigator=mock_navigator
    )

    # Simulate playing state
    orchestrator.deck_states["A"]["is_playing"] = True
    orchestrator.deck_states["B"]["is_playing"] = True

    # Cleanup
    orchestrator._cleanup()

    # Validate cleanup actions
    assert mock_midi.pause_deck.call_count == 2, "Both decks should be paused"
    assert mock_midi.set_crossfader.called_with(64), "Crossfader should be centered"
    assert mock_midi.set_volume.call_count == 2, "Both volumes should be reset"

    print(f"Pause calls: {mock_midi.pause_deck.call_count}")
    print(f"Crossfader reset: {mock_midi.set_crossfader.called}")
    print(f"Volume reset calls: {mock_midi.set_volume.call_count}")
    print("✅ TEST PASSED")
    return True


def run_all_tests():
    """Run all orchestrator tests"""
    print("\n" + "=" * 70)
    print("🧠 AUTONOMOUS ORCHESTRATOR TEST SUITE")
    print("=" * 70)

    tests = [
        test_initialization,
        test_start_session,
        test_state_transition_playing_to_loading,
        test_loading_track,
        test_mix_execution,
        test_error_handling,
        test_cleanup
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

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")

    return passed == total


if __name__ == "__main__":
    run_all_tests()
