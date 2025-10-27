"""
Browser Navigator - Vision-guided navigation in Traktor browser.

Uses Claude Vision API to read folder names and intelligently navigate
to target folders in the Traktor file browser tree.
"""

import time
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class BrowserNavigator:
    """
    Intelligent browser navigation using vision system.
    """

    def __init__(self, vision_system, ai_vision, midi_driver):
        """
        Initialize browser navigator.

        Args:
            vision_system: TraktorVisionSystem instance
            ai_vision: ClaudeVisionClient instance
            midi_driver: TraktorMIDIDriver instance
        """
        self.vision = vision_system
        self.ai = ai_vision
        self.midi = midi_driver

        logger.info("[BROWSER NAV] Browser navigator initialized")

    def get_current_browser_state(self) -> Dict:
        """
        Capture screenshot and analyze browser tree state.

        Returns:
            {
                'current_folder': str,
                'visible_folders': List[str],
                'tree_expanded': bool
            }
        """
        # Capture screenshot
        screenshot = self.vision.capture_traktor_window()

        # Ask Claude Vision to analyze browser tree
        vision_prompt = """Analyze the Traktor browser tree on the left side.

Focus on:
1. What is the currently selected/highlighted folder in the tree?
2. What folders are visible in the tree (expanded or collapsed)?
3. Is the tree expanded or collapsed?

Return ONLY JSON format:
{
    "current_folder": "name of currently selected folder or null",
    "visible_folders": ["folder1", "folder2", ...],
    "tree_expanded": true/false
}

Be precise with folder names. Common folders: Root, Collection, Playlists, iTunes, Audio Recordings, Dub, Techno, House, etc.
"""

        try:
            analysis = self.ai.analyze_traktor_screenshot(
                screenshot,
                custom_prompt=vision_prompt,
                verbose=False
            )

            # Extract browser info from analysis
            if isinstance(analysis, dict) and 'browser' in analysis:
                browser_state = analysis['browser']
            else:
                # Parse JSON from custom prompt
                browser_state = analysis

            logger.info(f"[BROWSER NAV] Current folder: {browser_state.get('current_folder')}")
            logger.info(f"[BROWSER NAV] Visible folders: {browser_state.get('visible_folders', [])}")

            return browser_state

        except Exception as e:
            logger.error(f"[BROWSER NAV] Error analyzing browser: {e}")
            return {
                'current_folder': None,
                'visible_folders': [],
                'tree_expanded': False
            }

    def navigate_to_folder(self, target_folder: str, max_attempts: int = 20) -> bool:
        """
        Navigate to target folder using vision-guided navigation.

        Algorithm:
        1. Capture current browser state
        2. Check if target folder is visible
        3. If visible, navigate to it
        4. If not visible, expand nodes and search
        5. Verify arrival at target

        Args:
            target_folder: Name of folder to navigate to (case-insensitive)
            max_attempts: Maximum navigation steps

        Returns:
            True if successfully navigated to target, False otherwise
        """
        target_lower = target_folder.lower()
        logger.info(f"[BROWSER NAV] Starting navigation to '{target_folder}'")

        for attempt in range(max_attempts):
            # First few attempts: aggressively expand nodes to reveal nested folders
            if attempt < 5:
                logger.info("[BROWSER NAV] Expansion phase - revealing nested folders...")
                # Expand current node
                self.midi.browser_expand_collapse()
                time.sleep(1.0)
                # Navigate down to next node
                self.midi.browser_navigate_down()
                time.sleep(0.5)
                # Expand that node too
                self.midi.browser_expand_collapse()
                time.sleep(1.0)

            logger.info(f"[BROWSER NAV] Attempt {attempt + 1}/{max_attempts}")

            # Get current state
            state = self.get_current_browser_state()
            current = state.get('current_folder', '').lower() if state.get('current_folder') else ''
            visible = [f.lower() for f in state.get('visible_folders', [])]

            # Check if we're already at target
            if current == target_lower:
                logger.info(f"[BROWSER NAV] ✓ Arrived at '{target_folder}'")
                return True

            # Check if target is visible in tree
            if target_lower in visible:
                logger.info(f"[BROWSER NAV] Target visible, navigating to it...")

                # Calculate how many steps to navigate
                try:
                    target_index = visible.index(target_lower)
                    current_index = visible.index(current) if current in visible else 0
                    steps = target_index - current_index

                    logger.info(f"[BROWSER NAV] Need {steps} steps")

                    # Navigate up or down
                    if steps > 0:
                        for _ in range(steps):
                            self.midi.browser_navigate_down()
                            time.sleep(0.3)
                    elif steps < 0:
                        for _ in range(abs(steps)):
                            self.midi.browser_navigate_up()
                            time.sleep(0.3)

                    # Verify arrival
                    time.sleep(0.5)
                    final_state = self.get_current_browser_state()
                    final_folder = final_state.get('current_folder', '').lower() if final_state.get('current_folder') else ''

                    if final_folder == target_lower:
                        logger.info(f"[BROWSER NAV] ✓ Successfully navigated to '{target_folder}'")
                        return True

                except (ValueError, IndexError) as e:
                    logger.warning(f"[BROWSER NAV] Error calculating navigation: {e}")

            # Target not visible, try expanding current node
            logger.info("[BROWSER NAV] Target not visible, expanding tree...")
            self.midi.browser_expand_collapse()
            time.sleep(1.0)  # Increased delay for UI update

            # Navigate down to explore deeper
            logger.info("[BROWSER NAV] Exploring: navigate down")
            self.midi.browser_navigate_down()
            time.sleep(0.5)

            # Try expanding the new node
            if attempt % 2 == 0:
                logger.info("[BROWSER NAV] Expanding new node")
                self.midi.browser_expand_collapse()
                time.sleep(1.0)

        logger.warning(f"[BROWSER NAV] Failed to find '{target_folder}' after {max_attempts} attempts")
        return False

    def search_and_navigate(self, search_terms: List[str], max_attempts: int = 15) -> Optional[str]:
        """
        Search for any of the given folder names and navigate to first match.

        Args:
            search_terms: List of folder names to search for (e.g., ['dub', 'Dub', 'DUB'])
            max_attempts: Maximum search attempts

        Returns:
            Name of folder found and navigated to, or None if not found
        """
        search_lower = [term.lower() for term in search_terms]
        logger.info(f"[BROWSER NAV] Searching for any of: {search_terms}")

        for attempt in range(max_attempts):
            state = self.get_current_browser_state()
            visible = state.get('visible_folders', [])

            # Check if any search term matches visible folders
            for folder in visible:
                if folder.lower() in search_lower:
                    logger.info(f"[BROWSER NAV] Found match: '{folder}'")
                    success = self.navigate_to_folder(folder, max_attempts=5)
                    if success:
                        return folder

            # Not found yet, expand and explore
            self.midi.browser_expand_collapse()
            time.sleep(0.5)
            self.midi.browser_navigate_down()
            time.sleep(0.3)

        logger.warning(f"[BROWSER NAV] Could not find any of: {search_terms}")
        return None


# Standalone test
if __name__ == "__main__":
    from autonomous_dj.generated.traktor_vision import TraktorVisionSystem
    from autonomous_dj.claude_vision_client import ClaudeVisionClient
    from traktor_midi_driver import TraktorMIDIDriver

    print("Testing Browser Navigator...")

    vision = TraktorVisionSystem()
    ai = ClaudeVisionClient()
    midi = TraktorMIDIDriver(dry_run=False)

    navigator = BrowserNavigator(vision, ai, midi)

    # Test 1: Get current state
    print("\nTest 1: Get current browser state")
    state = navigator.get_current_browser_state()
    print(f"Current folder: {state.get('current_folder')}")
    print(f"Visible folders: {state.get('visible_folders')}")

    # Test 2: Navigate to 'dub' folder
    print("\nTest 2: Navigate to 'dub' folder")
    success = navigator.navigate_to_folder('dub', max_attempts=10)
    print(f"Navigation {'succeeded' if success else 'failed'}")

    midi.close()
    print("Test complete")
