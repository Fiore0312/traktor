"""
Hierarchical Browser Navigator - Smart navigation through nested folder structures.

This module provides intelligent navigation that understands Traktor's folder hierarchy.
"""

import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class HierarchicalNavigator:
    """
    Navigates through Traktor browser using hierarchical path strategy.

    Example: To reach "Dub" which is at Explorer -> Music Folders -> C:/Users/.../Music -> Dub
    """

    def __init__(self, vision_system, ai_vision, midi_driver):
        self.vision = vision_system
        self.ai = ai_vision
        self.midi = midi_driver

    def navigate_to_nested_folder(self, target_folder: str, parent_hints: list = None) -> bool:
        """
        Navigate to a folder that might be nested deep in the tree.

        Args:
            target_folder: Name of target folder (e.g., "Dub")
            parent_hints: Optional list of parent folder names to look for
                         (e.g., ["Music Folders", "C:\\Users"])

        Returns:
            True if navigation successful
        """
        target_lower = target_folder.lower()
        logger.info(f"[HIERARCHICAL NAV] Navigating to '{target_folder}'")

        # Phase 1: Go to root
        logger.info("[HIERARCHICAL NAV] Phase 1: Going to root")
        for _ in range(15):
            self.midi.browser_navigate_up()
            time.sleep(0.2)

        # Phase 2: Expand all major nodes progressively
        logger.info("[HIERARCHICAL NAV] Phase 2: Expanding tree progressively")

        for depth in range(20):  # Try up to 20 levels deep
            logger.info(f"[HIERARCHICAL NAV] Depth {depth + 1}/20")

            # Get current state
            state = self._get_browser_state()
            current = state.get('current_folder', '').lower() if state.get('current_folder') else ''
            visible = [f.lower() for f in state.get('visible_folders', [])]

            logger.info(f"[HIERARCHICAL NAV] Current: {current}, Visible: {len(visible)} folders")

            # Check if target is visible
            if target_lower in visible:
                logger.info(f"[HIERARCHICAL NAV] Found '{target_folder}' in visible list!")
                return self._navigate_to_visible_folder(target_lower, visible, current)

            # Expand current node
            self.midi.browser_expand_collapse()
            time.sleep(1.0)

            # Navigate down to next node
            self.midi.browser_navigate_down()
            time.sleep(0.5)

        logger.warning(f"[HIERARCHICAL NAV] Could not find '{target_folder}' after exploring 20 levels")
        return False

    def _get_browser_state(self) -> Dict:
        """Capture and analyze browser state."""
        screenshot = self.vision.capture_traktor_window()

        vision_prompt = """Analyze the Traktor browser tree on the left side.

Return ONLY JSON format:
{
    "current_folder": "name of currently selected/highlighted folder or null",
    "visible_folders": ["folder1", "folder2", ...]
}

Be precise with folder names. Include ALL visible folders in the tree."""

        try:
            analysis = self.ai.analyze_traktor_screenshot(
                screenshot,
                custom_prompt=vision_prompt,
                verbose=False
            )

            if isinstance(analysis, dict) and 'browser' in analysis:
                return analysis['browser']
            else:
                return analysis
        except Exception as e:
            logger.error(f"[HIERARCHICAL NAV] Error analyzing browser: {e}")
            return {'current_folder': None, 'visible_folders': []}

    def _navigate_to_visible_folder(self, target_lower: str, visible: list, current: str) -> bool:
        """Navigate to a folder that is visible in the tree."""
        try:
            target_index = visible.index(target_lower)
            current_index = visible.index(current) if current in visible else 0
            steps = target_index - current_index

            logger.info(f"[HIERARCHICAL NAV] Need to move {steps} steps")

            if steps > 0:
                for _ in range(steps):
                    self.midi.browser_navigate_down()
                    time.sleep(0.3)
            elif steps < 0:
                for _ in range(abs(steps)):
                    self.midi.browser_navigate_up()
                    time.sleep(0.3)

            # Verify
            time.sleep(0.5)
            final_state = self._get_browser_state()
            final_folder = final_state.get('current_folder', '').lower() if final_state.get('current_folder') else ''

            if final_folder == target_lower:
                logger.info(f"[HIERARCHICAL NAV] ✓ Successfully reached '{target_lower}'")
                return True
            else:
                logger.warning(f"[HIERARCHICAL NAV] Ended at '{final_folder}' instead of '{target_lower}'")
                return False

        except (ValueError, IndexError) as e:
            logger.error(f"[HIERARCHICAL NAV] Navigation error: {e}")
            return False
