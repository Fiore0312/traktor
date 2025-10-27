"""
Autonomous Browser Navigator for Traktor Pro 3
Provides intelligent, position-tracked navigation through Traktor's browser.
Uses MIDI CC commands with timing delays to ensure reliable operation.
"""

import time
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from traktor_midi_driver import TraktorMIDIDriver

class AutonomousBrowserNavigator:
    """
    Handles autonomous navigation in Traktor browser without computer vision.
    Uses position tracking and MIDI commands for reliable folder/track selection.
    """

    def __init__(self, midi_driver: TraktorMIDIDriver, state_manager=None):
        self.midi = midi_driver
        self.state_manager = state_manager
        self.folder_structure_file = Path("data/folder_structure.json")
        self.current_position = {"tree": 0, "track": 0}
        self.folder_map = self._load_folder_structure()

        # MIDI CC values from traktor_midi_driver.py
        # Browser.Tree (folders/left panel):
        self.CC_TREE_DOWN = 72  # BROWSER_SCROLL_TREE_INC
        self.CC_TREE_UP = 73    # BROWSER_SCROLL_TREE_DEC

        # Browser.List (tracks/right panel):
        self.CC_TRACK_SCROLL_DOWN = 74  # BROWSER_SCROLL_LIST (Inc)
        self.CC_TRACK_SCROLL_UP = 92    # BROWSER_SCROLL_LIST_UP (Dec)

        # General:
        self.CC_EXPAND_COLLAPSE = 64  # BROWSER_EXPAND_COLLAPSE

        # Critical timing for Traktor responsiveness
        self.TREE_NAV_DELAY = 0.8  # seconds between tree navigation commands (reduced from 1.8)
        self.TRACK_NAV_DELAY = 0.2  # seconds between track scroll commands (reduced from 0.3)

    def _load_folder_structure(self) -> Dict:
        """Load folder structure from JSON file."""
        if self.folder_structure_file.exists():
            with open(self.folder_structure_file, 'r') as f:
                return json.load(f)
        return {"folders": {}, "navigation_history": []}

    def _save_folder_structure(self):
        """Save current folder structure to JSON."""
        self.folder_structure_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.folder_structure_file, 'w') as f:
            json.dump(self.folder_map, f, indent=2)

    def _send_midi_with_delay(self, cc: int, value: int, delay: float):
        """Send MIDI CC and wait for Traktor to process."""
        self.midi.send_cc(cc, value)
        time.sleep(delay)

    def reset_to_root(self) -> bool:
        """
        Navigate to root of browser tree AND collapse all folders.

        IMPORTANT: This also collapses all expanded folders to prevent
        auto-expansion during navigation (which shifts positions).

        Strategy:
        1. Send tree UP 20 times to reach root
        2. Send COLLAPSE 20 times to close all expanded folders

        Returns: True if successful
        """
        print("Resetting browser to root position...")

        # Step 1: Navigate to root
        for i in range(20):  # Enough to reach root from any position
            self._send_midi_with_delay(self.CC_TREE_UP, 127, 0.2)

        time.sleep(0.3)

        # Step 2: Collapse ALL expanded folders
        # This prevents auto-expansion during DOWN navigation
        print("  Collapsing all expanded folders...")
        for i in range(15):  # Collapse multiple times to ensure all closed
            self._send_midi_with_delay(self.CC_EXPAND_COLLAPSE, 127, 0.2)

        # After reset, we're definitely at position 0 with all collapsed
        self.current_position["tree"] = 0
        self._update_state("browser_tree_position", 0)

        print("Browser reset to root (all folders collapsed)")
        return True

    def navigate_to_folder(self, folder_name: str) -> Tuple[bool, str]:
        """
        Navigate to a specific music folder (House, Dub, etc.).

        NEW: Handles multi-level hierarchy automatically.
        Path: ROOT -> Explorer -> Music Folders -> C:\\Users\\Utente\\Music -> [folder]

        Args:
            folder_name: Name of music folder (e.g., "House", "Dub", "Deep House")

        Returns:
            (success: bool, message: str)
        """
        # Load complete folder structure
        complete_structure_path = Path("data/folder_structure_COMPLETE.json")
        if complete_structure_path.exists():
            with open(complete_structure_path, 'r') as f:
                complete_structure = json.load(f)
                music_folders = complete_structure.get("music_folders", {})
        else:
            # Fallback to old structure
            music_folders = self.folder_map.get("folders", {})

        # Map "Techno" to "House" if not found
        if folder_name == "Techno" and folder_name not in music_folders:
            print("[!]  'Techno' folder not found - using 'House' as alternative")
            folder_name = "House"

        # Check if folder exists
        if folder_name not in music_folders:
            return False, f"[FAIL] Folder '{folder_name}' not found in music folders"

        # Get target position within music folders
        target_position = music_folders[folder_name]["position"]

        # Step 1: Navigate to music root (multi-level)
        print(f"\n>> Navigating to '{folder_name}' (position {target_position} in music folders)...")
        success, msg = self.navigate_to_music_root()
        if not success:
            return False, f"Failed to reach music root: {msg}"

        # Step 2: Navigate to specific folder
        print(f"  -> Scrolling to '{folder_name}' ({target_position} steps DOWN)...")
        for step in range(target_position):
            self._send_midi_with_delay(self.CC_TREE_DOWN, 127, self.TREE_NAV_DELAY)
            self.current_position["tree"] = step + 1
            if (step + 1) % 5 == 0 or step == target_position - 1:
                print(f"     Step {step + 1}/{target_position}")

        # Step 3: Expand folder
        print(f"  -> Expanding '{folder_name}'...")
        self._send_midi_with_delay(self.CC_EXPAND_COLLAPSE, 127, 0.5)
        time.sleep(0.5)

        # Update state
        self._update_state("current_folder", folder_name)
        self._update_state("browser_tree_position", target_position)

        # Log navigation
        if "navigation_history" not in self.folder_map:
            self.folder_map["navigation_history"] = []

        self.folder_map["navigation_history"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "folder": folder_name,
            "position": target_position
        })
        self._save_folder_structure()

        print(f"[OK] Navigated to folder '{folder_name}'")
        return True, f"Navigated to {folder_name}"

    def scroll_to_track(self, track_number: int, current_track: int = 0) -> Tuple[bool, str]:
        """
        Scroll to specific track number in current folder.

        Args:
            track_number: Target track (1-based index)
            current_track: Current track position (default: 0 = top)

        Returns:
            (success: bool, message: str)
        """
        if track_number < 1:
            return False, "[FAIL] Track number must be >= 1"

        # Calculate steps needed
        steps = track_number - current_track - 1

        if steps == 0:
            print(f"[OK] Already at track {track_number}")
            return True, f"At track {track_number}"

        print(f">> Scrolling to track {track_number}...")

        # Browser.List navigation (verified from user screenshots - 2025-10-27):
        # CC 74 = scroll DOWN (next track)
        # CC 92 = scroll UP (previous track)

        if steps > 0:
            # Scroll DOWN
            for i in range(steps):
                self._send_midi_with_delay(self.CC_TRACK_SCROLL_DOWN, 127, self.TRACK_NAV_DELAY)
                print(f"   Track scroll DOWN {i+1}/{steps}")
        else:
            # Scroll UP
            for i in range(abs(steps)):
                self._send_midi_with_delay(self.CC_TRACK_SCROLL_UP, 127, self.TRACK_NAV_DELAY)
                print(f"   Track scroll UP {i+1}/{abs(steps)}")

        # Update state
        self.current_position["track"] = track_number
        self._update_state("browser_track_position", track_number)

        print(f"[OK] Scrolled to track {track_number}")
        return True, f"At track {track_number}"

    def navigate_and_select_track(self, folder_name: str, track_number: int) -> Tuple[bool, str]:
        """
        Complete navigation: folder + track selection.

        Args:
            folder_name: Target folder
            track_number: Target track in that folder

        Returns:
            (success: bool, message: str)
        """
        # Step 1: Navigate to folder
        success, msg = self.navigate_to_folder(folder_name)
        if not success:
            return False, msg

        # Step 2: Scroll to track
        success, msg = self.scroll_to_track(track_number, current_track=0)
        if not success:
            return False, msg

        return True, f"Selected track {track_number} in {folder_name}"

    def _update_state(self, key: str, value):
        """Update state manager if available."""
        if self.state_manager:
            try:
                current_state = self.state_manager.get_state()
                if "browser_state" not in current_state.__dict__:
                    # Add browser_state dynamically
                    current_state.__dict__["browser_state"] = {}
                current_state.__dict__["browser_state"][key] = value

                # Update via dict
                state_dict = current_state.to_dict()
                if "browser_state" not in state_dict:
                    state_dict["browser_state"] = {}
                state_dict["browser_state"][key] = value

                self.state_manager._write_state(state_dict)
            except Exception as e:
                print(f"[!] Warning: Could not update state: {e}")

    def navigate_to_music_root(self) -> Tuple[bool, str]:
        """
        Navigate to music root (genre folders level).

        CORRECT hierarchy (verified with user screenshots 2025-10-27):
        ROOT -> 10 DOWN -> Explorer -> Expand
            -> 2 DOWN -> Music Folders -> Expand
            -> 1 DOWN -> C:\\Users\\Utente\\Music -> Expand
            -> GENRE FOLDERS (Ableton, Acid Jazz, House, Dub, etc.)

        CRITICAL: After collapse-all, Explorer is at position 10 (not 7!)
        This is because "All Remix Sets (6)" and other folders are collapsed.

        Music Folders contains C:\\Users\\Utente\\Music as first item, which must be expanded
        to see the genre folders!

        Returns:
            (success: bool, message: str)
        """
        print("\n>> Navigating to music root (multi-level)...")

        # Step 1: Reset to ROOT
        print("  Step 1/7: Reset to root...")
        self.reset_to_root()
        time.sleep(0.3)  # Pause after reset (reduced from 1.0)

        # Step 2: Navigate to Explorer (10 DOWN from root - verified by user)
        print("  Step 2/7: Navigate to Explorer (10 steps DOWN)...")
        for i in range(10):
            self._send_midi_with_delay(self.CC_TREE_DOWN, 127, self.TREE_NAV_DELAY)
            if (i + 1) % 5 == 0 or i == 9:
                print(f"    -> {i+1}/10")
        time.sleep(0.3)

        # Step 3: Expand Explorer
        print("  Step 3/7: Expand Explorer...")
        self._send_midi_with_delay(self.CC_EXPAND_COLLAPSE, 127, 0.3)
        time.sleep(0.3)

        # Step 4: Navigate to Music Folders (2 DOWN from Explorer - verified by user)
        print("  Step 4/7: Navigate to Music Folders (2 steps DOWN)...")
        for i in range(2):
            self._send_midi_with_delay(self.CC_TREE_DOWN, 127, self.TREE_NAV_DELAY)
        time.sleep(0.3)

        # Step 5: Expand Music Folders (simple single expand - no double-collapse trick)
        print("  Step 5/7: Expand Music Folders...")
        self._send_midi_with_delay(self.CC_EXPAND_COLLAPSE, 127, 0.3)
        time.sleep(0.3)

        # Step 6: Navigate DOWN to C:\Users\Utente\Music (1 DOWN - it's the first item)
        print("  Step 6/7: Navigate to C:\\Users\\Utente\\Music (1 step DOWN)...")
        self._send_midi_with_delay(self.CC_TREE_DOWN, 127, self.TREE_NAV_DELAY)
        time.sleep(0.3)

        # Step 7: Expand C:\Users\Utente\Music
        print("  Step 7/7: Expand C:\\Users\\Utente\\Music...")
        self._send_midi_with_delay(self.CC_EXPAND_COLLAPSE, 127, 0.3)
        time.sleep(0.5)  # Final pause to let browser stabilize

        # DONE! After expanding Music Folders, we are DIRECTLY at genre folders

        # Update state
        self._update_state("at_music_root", True)
        self._update_state("current_folder", "MUSIC_ROOT")

        print("[OK] Navigation to music root complete!")
        print("   Now at genre folders level (Ableton, Acid Jazz, House, Dub, etc.)")

        return True, "At music root"

    def get_current_position(self) -> Dict:
        """Get current browser position."""
        return {
            "tree_position": self.current_position["tree"],
            "track_position": self.current_position["track"],
            "folder_map": self.folder_map
        }
