"""
Test suite for Autonomous Browser Navigator
Tests navigation to folders and track selection.

NOTE: These tests require Traktor Pro 3 running with MIDI enabled.
They are designed to be run manually, not in CI/CD.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from traktor_midi_driver import TraktorMIDIDriver
from autonomous_dj.generated.autonomous_browser_navigator import AutonomousBrowserNavigator


def test_reset_to_root():
    """Test: Reset browser to root position"""
    print("\n🧪 TEST 1: Reset to Root")
    print("=" * 50)

    midi = TraktorMIDIDriver()
    navigator = AutonomousBrowserNavigator(midi)

    success = navigator.reset_to_root()

    if success:
        print("✅ TEST PASSED: Reset to root successful")
    else:
        print("❌ TEST FAILED: Could not reset to root")

    return success


def test_navigate_to_techno():
    """Test: Navigate to Techno folder"""
    print("\n🧪 TEST 2: Navigate to Techno Folder")
    print("=" * 50)

    midi = TraktorMIDIDriver()
    navigator = AutonomousBrowserNavigator(midi)

    success, msg = navigator.navigate_to_folder("Techno")
    print(f"Result: {msg}")

    if success:
        print("✅ TEST PASSED: Navigated to Techno")
    else:
        print("❌ TEST FAILED: Could not navigate to Techno")

    return success


def test_navigate_to_dub():
    """Test: Navigate to Dub folder"""
    print("\n🧪 TEST 3: Navigate to Dub Folder")
    print("=" * 50)

    midi = TraktorMIDIDriver()
    navigator = AutonomousBrowserNavigator(midi)

    success, msg = navigator.navigate_to_folder("Dub")
    print(f"Result: {msg}")

    if success:
        print("✅ TEST PASSED: Navigated to Dub")
    else:
        print("❌ TEST FAILED: Could not navigate to Dub")

    return success


def test_scroll_to_track():
    """Test: Scroll to track #5 in current folder"""
    print("\n🧪 TEST 4: Scroll to Track #5")
    print("=" * 50)

    midi = TraktorMIDIDriver()
    navigator = AutonomousBrowserNavigator(midi)

    # First navigate to a folder
    navigator.navigate_to_folder("Techno")

    # Then scroll to track 5
    success, msg = navigator.scroll_to_track(5, current_track=0)
    print(f"Result: {msg}")

    if success:
        print("✅ TEST PASSED: Scrolled to track #5")
    else:
        print("❌ TEST FAILED: Could not scroll to track")

    return success


def test_complete_navigation():
    """Test: Complete navigation (folder + track)"""
    print("\n🧪 TEST 5: Complete Navigation (Dub folder, track 3)")
    print("=" * 50)

    midi = TraktorMIDIDriver()
    navigator = AutonomousBrowserNavigator(midi)

    success, msg = navigator.navigate_and_select_track("Dub", 3)
    print(f"Result: {msg}")

    if success:
        print("✅ TEST PASSED: Complete navigation successful")
    else:
        print("❌ TEST FAILED: Navigation failed")

    return success


def run_all_tests():
    """Run all navigation tests"""
    print("\n" + "=" * 70)
    print("🚀 AUTONOMOUS NAVIGATION TEST SUITE")
    print("=" * 70)

    tests = [
        test_reset_to_root,
        test_navigate_to_techno,
        test_navigate_to_dub,
        test_scroll_to_track,
        test_complete_navigation
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
            time.sleep(2)  # Pause between tests
        except Exception as e:
            print(f"❌ TEST ERROR: {test_func.__name__} - {e}")
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
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ SOME TESTS FAILED - Review output above")

    return passed == total


if __name__ == "__main__":
    print("\n⚠️  IMPORTANT: Make sure Traktor Pro 3 is running before starting tests!\n")
    input("Press ENTER to continue...")

    run_all_tests()
