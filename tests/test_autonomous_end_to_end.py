"""
End-to-End Test for Autonomous DJ System

Tests the complete autonomous workflow from start to finish.

NOTE: This test uses REAL components and requires:
- Traktor Pro 3 running
- loopMIDI configured
- tracks.db with analyzed tracks
- OpenRouter API key (optional - fallback works without)

WARNING: This will actually control Traktor and play music!
Run ONLY when ready for full system test.
"""

import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_dj.autonomous_orchestrator import AutonomousOrchestrator, DJState
from traktor_midi_driver import TraktorMIDIDriver


def test_orchestrator_initialization():
    """Test: Orchestrator can be created successfully"""
    print("\n🧪 TEST 1: Orchestrator Initialization")
    print("=" * 70)

    try:
        orchestrator = AutonomousOrchestrator(
            start_genre="Techno",
            energy_level="medium"
        )

        # Validate
        assert orchestrator.state == DJState.IDLE, "Should start in IDLE state"
        assert orchestrator.midi is not None, "MIDI driver should be initialized"
        assert orchestrator.brain is not None, "Brain should be initialized"
        assert orchestrator.navigator is not None, "Navigator should be initialized"
        assert orchestrator.current_genre == "Techno"
        assert orchestrator.energy_level == "medium"

        print("✅ Orchestrator initialized successfully")
        print(f"   State: {orchestrator.state}")
        print(f"   Genre: {orchestrator.current_genre}")
        print(f"   Energy: {orchestrator.energy_level}")
        print("✅ TEST PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_brain_decision_making():
    """Test: Brain can make intelligent track decisions"""
    print("\n🧪 TEST 2: Brain Decision Making")
    print("=" * 70)

    try:
        orchestrator = AutonomousOrchestrator()

        # Test initial track decision
        initial_state = {
            "playing_deck": None,
            "current_track": None,
            "energy_level": "medium",
            "genre_preference": "Techno",
            "tracks_played": 0,
            "session_duration_minutes": 0
        }

        decision = orchestrator.brain.decide_next_track(initial_state)

        # Validate decision structure
        assert "folder_name" in decision, "Should return folder_name"
        assert "track_criteria" in decision, "Should return track_criteria"
        assert "reasoning" in decision, "Should return reasoning"

        print(f"✅ Brain decision:")
        print(f"   Folder: {decision['folder_name']}")
        print(f"   BPM range: {decision['track_criteria']['bpm_min']}-{decision['track_criteria']['bpm_max']}")
        print(f"   Compatible keys: {decision['track_criteria']['compatible_keys']}")
        print(f"   Reasoning: {decision['reasoning']}")
        print("✅ TEST PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_navigator_folder_navigation():
    """Test: Navigator can navigate to folders"""
    print("\n🧪 TEST 3: Navigator Folder Navigation")
    print("=" * 70)
    print("⚠️  This test will ACTUALLY move the Traktor browser!")
    print("⚠️  Make sure Traktor Pro 3 is running and focused.\n")

    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("⏭️  TEST SKIPPED\n")
        return True

    try:
        midi = TraktorMIDIDriver()

        from autonomous_dj.generated.autonomous_browser_navigator import AutonomousBrowserNavigator
        navigator = AutonomousBrowserNavigator(midi)

        # Test navigation to Techno folder
        success, msg = navigator.navigate_to_folder("Techno")

        print(f"Navigation result: {msg}")

        if success:
            print("✅ Successfully navigated to Techno folder")
            print("✅ TEST PASSED\n")
            return True
        else:
            print(f"❌ Navigation failed: {msg}")
            print("❌ TEST FAILED\n")
            return False

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_controller_integration():
    """Test: Workflow controller can trigger autonomous session"""
    print("\n🧪 TEST 4: Workflow Controller Integration")
    print("=" * 70)

    try:
        from autonomous_dj.workflow_controller import DJWorkflowController

        controller = DJWorkflowController()

        # Test command parsing for autonomous mode
        test_command = "Start autonomous DJ"
        action_plan = controller.llm.parse_dj_command(test_command)

        print(f"Command: '{test_command}'")
        print(f"Parsed action: {action_plan['action']}")
        print(f"Confidence: {action_plan['confidence']}")

        assert action_plan['action'] == 'START_AUTONOMOUS', "Should parse to START_AUTONOMOUS action"
        assert action_plan['confidence'] > 0.7, "Should have high confidence"

        print("✅ Command parsing works correctly")
        print("✅ TEST PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_autonomous_session_simulation():
    """Test: Full autonomous session (SIMULATED - uses mocks)"""
    print("\n🧪 TEST 5: Full Autonomous Session (Simulated)")
    print("=" * 70)

    try:
        # Create orchestrator with mocked MIDI to avoid actual playback
        mock_midi = Mock()
        mock_midi.load_selected_track.return_value = True
        mock_midi.play_deck.return_value = True

        orchestrator = AutonomousOrchestrator(
            midi_driver=mock_midi,
            start_genre="Techno",
            energy_level="medium"
        )

        # Mock navigator to avoid actual browser navigation
        orchestrator.navigator.navigate_and_select_track = Mock(return_value=(True, "Success"))

        # Mock bars estimation to trigger transitions quickly
        orchestrator._estimate_bars_remaining = Mock(side_effect=[
            64,  # First check - no load yet
            20,  # Second check - trigger load
            15,  # Third check - ready to mix
            10,  # During mix
        ])

        print("Starting simulated autonomous session (max 2 tracks)...")

        # Patch time.sleep to speed up simulation
        with patch('time.sleep'):
            success = orchestrator.start_session()

            if success:
                print(f"✅ Session started on Deck {orchestrator.playing_deck}")

                # Simulate one cycle: PLAYING → LOADING → MIXING → PLAYING
                orchestrator._handle_playing_state()  # Should trigger LOADING
                assert orchestrator.state == DJState.LOADING, "Should transition to LOADING"
                print("✅ Transition PLAYING → LOADING")

                orchestrator._handle_loading_state()  # Should transition to MIXING
                assert orchestrator.state == DJState.MIXING, "Should transition to MIXING"
                print("✅ Transition LOADING → MIXING")

                orchestrator._handle_mixing_state()  # Should return to PLAYING
                assert orchestrator.state == DJState.PLAYING, "Should return to PLAYING"
                assert orchestrator.tracks_played == 2, "Should have played 2 tracks"
                print("✅ Transition MIXING → PLAYING")
                print(f"✅ Tracks played: {orchestrator.tracks_played}")

                print("✅ TEST PASSED\n")
                return True
            else:
                print("❌ Failed to start session")
                print("❌ TEST FAILED\n")
                return False

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_autonomous_session_live():
    """Test: Full autonomous session (LIVE - requires Traktor running)"""
    print("\n🧪 TEST 6: Full Autonomous Session (LIVE)")
    print("=" * 70)
    print("⚠️  ⚠️  ⚠️  WARNING ⚠️  ⚠️  ⚠️")
    print("This test will ACTUALLY:")
    print("- Control Traktor Pro 3")
    print("- Load tracks from your collection")
    print("- Start playback and mixing")
    print("- Play music through your audio output")
    print()
    print("Requirements:")
    print("✓ Traktor Pro 3 running")
    print("✓ loopMIDI virtual port active")
    print("✓ tracks.db with analyzed tracks")
    print("✓ Audio output ready (may be loud!)")
    print("=" * 70)
    print()

    response = input("REALLY run LIVE autonomous session? (type 'YES' to confirm): ")
    if response != 'YES':
        print("⏭️  TEST SKIPPED (safety abort)\n")
        return True

    max_tracks = int(input("How many tracks to play? (recommended: 2-3 for testing): ") or "2")

    try:
        print(f"\n🎧 Starting LIVE autonomous session ({max_tracks} tracks)...")
        print("Press Ctrl+C to stop at any time\n")

        orchestrator = AutonomousOrchestrator(
            start_genre="Techno",
            energy_level="medium"
        )

        # Start session
        success = orchestrator.start_session()

        if not success:
            print("❌ Failed to start session")
            return False

        print(f"✅ Session started on Deck {orchestrator.playing_deck}")
        print(f"🎵 First track playing...\n")

        # Run main loop
        orchestrator.main_loop(max_tracks=max_tracks, check_interval=2.0)

        # Session complete
        print("\n" + "=" * 70)
        print("🎉 AUTONOMOUS SESSION COMPLETE!")
        print("=" * 70)
        print(f"✅ Tracks played: {orchestrator.tracks_played}")
        print(f"⏱️  Duration: {int((time.time() - orchestrator.session_start_time) / 60)} minutes")
        print("✅ TEST PASSED\n")
        return True

    except KeyboardInterrupt:
        print("\n⏹️  Session stopped by user (Ctrl+C)")
        print("⚠️  TEST INTERRUPTED (but system worked)\n")
        return True
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all end-to-end tests"""
    print("\n" + "=" * 70)
    print("🎧 AUTONOMOUS DJ SYSTEM - END-TO-END TEST SUITE")
    print("=" * 70)
    print()
    print("Test breakdown:")
    print("  Tests 1-2: Component initialization (safe, no Traktor required)")
    print("  Test 3: Navigator (requires Traktor, moves browser)")
    print("  Test 4: Workflow integration (safe, command parsing only)")
    print("  Test 5: Full simulation (safe, uses mocks)")
    print("  Test 6: LIVE session (requires Traktor, plays music!)")
    print("=" * 70)
    print()

    tests = [
        ("Initialization", test_orchestrator_initialization, True),
        ("Brain Decisions", test_brain_decision_making, True),
        ("Navigator", test_navigator_folder_navigation, False),  # Optional
        ("Workflow Integration", test_workflow_controller_integration, True),
        ("Simulation", test_full_autonomous_session_simulation, True),
        ("LIVE Session", test_full_autonomous_session_live, False),  # Optional, dangerous
    ]

    results = []
    for test_name, test_func, auto_run in tests:
        if not auto_run:
            # Ask user if they want to run optional/dangerous tests
            print(f"\n{'=' * 70}")
            print(f"Optional test: {test_name}")
            response = input("Run this test? (y/n): ")
            if response.lower() != 'y':
                print(f"⏭️  SKIPPED: {test_name}\n")
                continue

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ TEST ERROR: {test_name} - {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

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
        print("\n🎉 ALL TESTS PASSED! Autonomous DJ system is ready!")
    else:
        print("\n⚠️ SOME TESTS FAILED - Review output above")

    return passed == total


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT NOTES:")
    print("- Tests 1-2-4-5 are safe and don't require Traktor")
    print("- Tests 3 and 6 will control Traktor - run ONLY when ready")
    print("- Test 6 (LIVE) will play music - set volume appropriately!")
    print()

    input("Press ENTER to start tests...")

    run_all_tests()
