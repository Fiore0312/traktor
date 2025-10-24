#!/usr/bin/env python3
"""
VISION-GUIDED TRACK LOADING - DEMO
===================================
Demonstrates vision-guided workflow:
1. Capture Traktor screenshot
2. Claude analyzes the image
3. Decide appropriate MIDI commands
4. Execute and verify with new screenshot

This script shows the complete loop for autonomous navigation.
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from autonomous_dj.generated.traktor_vision import TraktorVisionSystem
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC


def vision_guided_track_load():
    """
    Complete vision-guided workflow for loading a track
    """
    print("=" * 70)
    print("VISION-GUIDED TRACK LOADING - DEMONSTRATION")
    print("=" * 70)
    
    # Initialize systems
    print("\n[1/6] Initializing Vision System...")
    vision = TraktorVisionSystem()
    
    print("[2/6] Initializing MIDI Driver...")
    try:
        midi = TraktorMIDIDriver()
        print(f"[OK] Connected to: {midi.port_name}")
    except Exception as e:
        print(f"[ERROR] MIDI connection failed: {e}")
        print("Make sure Traktor and loopMIDI are running!")
        return
    
    # Step 1: Capture current state
    print("\n[3/6] Capturing Traktor screenshot...")
    try:
        screenshot_path = vision.capture_traktor_window()
        print(f"[OK] Screenshot captured: {screenshot_path}")
    except Exception as e:
        print(f"[ERROR] Screenshot failed: {e}")
        return
    
    # Step 2: Prepare for Claude analysis
    print("\n[4/6] Preparing screenshot for Claude analysis...")
    metadata = vision.prepare_for_analysis()
    
    print("\n" + "=" * 70)
    print("[READY] SCREENSHOT READY FOR CLAUDE")
    print("=" * 70)
    print(f"Path: {metadata['screenshot_path']}")
    print(f"Timestamp: {metadata['timestamp']}")
    print("\n[CLAUDE] INSTRUCTIONS FOR CLAUDE:")
    print(metadata['instructions'])
    print("=" * 70)
    
    # Step 3: Get analysis from Claude (simulated here)
    print("\n[5/6] Waiting for Claude's visual analysis...")
    print("\n[INFO] In Claude Code, you would now:")
    print("   1. Use 'view' tool to read the screenshot")
    print("   2. Claude analyzes the Traktor UI")
    print("   3. Claude provides JSON analysis")
    print("   4. Script uses analysis to decide MIDI commands")

    # Example of what Claude might return
    print("\n[EXAMPLE] EXAMPLE CLAUDE ANALYSIS:")
    example_analysis = {
        "selected_folder": "Dub",
        "track_highlighted": True,
        "track_number": 3,
        "track_name": "An Airbag Saved My Dub (Bonus Track)",
        "artist": "Easy Star All-Stars",
        "bpm": 85.11,
        "genre": "Reggae",
        "deck_a_status": "empty",
        "deck_b_status": "empty",
        "ready_to_load": True
    }
    
    import json
    print(json.dumps(example_analysis, indent=2))
    
    # Step 4: Decide MIDI commands based on analysis
    print("\n[6/6] Determining MIDI commands from analysis...")
    recommendations = vision.analyze_browser_position(example_analysis)
    
    print("\n[ACTIONS] RECOMMENDED ACTIONS:")
    print(json.dumps(recommendations, indent=2))

    # Step 5: Execute MIDI commands (optional, commented for safety)
    print("\n[DISABLED] MIDI EXECUTION (DISABLED FOR DEMO)")
    print("To actually execute, uncomment the code below:")
    print("""
    if recommendations['can_load_track']:
        print("\\n[EXEC] Executing: Load track to Deck A...")
        midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
        time.sleep(0.5)
        
        # Capture screenshot to verify
        print("[VERIFY] Capturing verification screenshot...")
        verify_screenshot = vision.capture_traktor_window()
        print(f"[OK] Verification screenshot: {verify_screenshot}")
        print("\\n[CHECK] Now Claude can verify the track loaded correctly!")
    """)
    
    # Cleanup
    print("\n[CLEANUP] Cleaning up old screenshots (keeping last 10)...")
    vision.cleanup_old_screenshots(keep_last_n=10)

    print("\n" + "=" * 70)
    print("[OK] DEMO COMPLETE!")
    print("=" * 70)
    print("\n[NEXT] NEXT STEPS:")
    print("1. Use Claude Code to analyze the screenshot")
    print("2. Let Claude decide the MIDI commands")
    print("3. Execute commands and verify with new screenshot")
    print("4. Repeat the loop until track is loaded and playing")
    print("\n[RESULT] This creates a vision-guided autonomous workflow!")
    print("=" * 70)
    
    midi.close()


if __name__ == "__main__":
    vision_guided_track_load()
