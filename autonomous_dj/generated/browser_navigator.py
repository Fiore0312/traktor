#!/usr/bin/env python3
"""
Browser Navigator Module - Traktor Pro 3 Browser Control
=========================================================

Provides programmatic control of Traktor's browser for autonomous track selection.

Features:
- Track list scrolling (CC 74)
- Folder tree navigation (CC 72, 73)
- Folder expand/collapse (CC 64)
- Integration with music-vision-navigator for visual positioning

Author: AI DJ System - Browser Navigation Discovery
Date: 2025-01-11
Version: 1.0.0

Knowledge Base: browser_navigation_knowledge.json
Verified: Windows + loopMIDI + Traktor Pro 3
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional, List
from enum import IntEnum

# Add parent directory to path to import traktor_midi_driver
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from traktor_midi_driver import TraktorMIDIDriver

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# MIDI CC MAPPING (VERIFIED 2025-01-11)
# ============================================================================

class BrowserCC(IntEnum):
    """Traktor Pro 3 Browser Navigation CC Assignments - VERIFIED"""
    SCROLL_LIST = 74        # Scroll track list up/down
    TREE_NAVIGATE_DOWN = 72 # Navigate folder tree down
    TREE_NAVIGATE_UP = 73   # Navigate folder tree up
    EXPAND_COLLAPSE = 64    # Expand/collapse folder


# ============================================================================
# GLOBAL STATE
# ============================================================================

# MIDI driver instance (module-level singleton)
_midi_driver = None


def get_midi_driver() -> TraktorMIDIDriver:
    """
    Get or create MIDI driver instance (singleton pattern)

    Returns:
        TraktorMIDIDriver instance
    """
    global _midi_driver
    if _midi_driver is None:
        _midi_driver = TraktorMIDIDriver()
        logger.info("TraktorMIDIDriver initialized for browser navigation")
    return _midi_driver


# ============================================================================
# MIDI COMMUNICATION
# ============================================================================

def send_midi_cc(cc_number: int, value: int) -> bool:
    """
    Send MIDI CC command to Traktor via TraktorMIDIDriver

    Args:
        cc_number: MIDI CC number (0-127)
        value: MIDI value (0-127)

    Returns:
        True if MIDI command sent successfully

    Raises:
        RuntimeError: If MIDI communication fails
    """
    try:
        driver = get_midi_driver()
        success = driver.send_cc(cc_number, value)

        if not success:
            logger.error(
                f"MIDI command failed: CC {cc_number} = {value}",
                extra={'cc_number': cc_number, 'value': value}
            )
            raise RuntimeError(f"MIDI command failed: CC {cc_number} = {value}")

        logger.debug(
            f"Browser MIDI sent: CC {cc_number} = {value}",
            extra={'cc_number': cc_number, 'value': value}
        )
        return True

    except Exception as e:
        logger.error(
            f"MIDI communication error: {str(e)}",
            extra={'cc_number': cc_number, 'error': str(e)}
        )
        raise


# ============================================================================
# BROWSER NAVIGATION FUNCTIONS
# ============================================================================

def scroll_list(amount: int = 1) -> bool:
    """
    Scroll track list in Traktor browser

    Args:
        amount: Scroll amount (1-127)
                Values 1-63: Scroll down
                Values 64-127: Scroll up (experimental)

    Returns:
        True if command sent successfully

    Example:
        >>> scroll_list(1)   # Scroll down 1 item
        >>> scroll_list(5)   # Scroll down ~5 items
        >>> scroll_list(127) # Scroll up (if supported)
    """
    amount = max(1, min(127, amount))
    success = send_midi_cc(BrowserCC.SCROLL_LIST, amount)

    if success:
        logger.info(f"Browser list scrolled: value={amount}")

    return success


def scroll_down(items: int = 1, delay_sec: float = 1.5) -> bool:
    """
    Scroll down in track list

    IMPORTANT: Traktor requires time to process each scroll command.
    Default delay is 1.5 seconds per scroll step.

    Args:
        items: Number of items to scroll (1-63)
        delay_sec: Delay after each scroll step (default: 1.5s)
                   Set to 0 to disable delay (not recommended)

    Returns:
        True if command sent successfully

    Example:
        >>> scroll_down(1)              # Scroll 1 item with 1.5s delay
        >>> scroll_down(3, delay_sec=2) # Scroll 3 items with 2s delay each
        >>> scroll_down(5, delay_sec=0) # Fast scroll (may miss items)
    """
    items = max(1, min(63, items))

    # For multiple items, scroll one at a time with delay
    if items > 1 and delay_sec > 0:
        success = True
        for i in range(items):
            if not scroll_list(1):
                success = False
                break
            if i < items - 1:  # Don't delay after last scroll
                time.sleep(delay_sec)
        return success
    else:
        return scroll_list(items)


def scroll_up(items: int = 1, delay_sec: float = 1.5) -> bool:
    """
    Scroll up in track list (experimental)

    IMPORTANT: Traktor requires time to process each scroll command.
    Default delay is 1.5 seconds per scroll step.

    Args:
        items: Number of items to scroll (1-63)
        delay_sec: Delay after each scroll step (default: 1.5s)

    Returns:
        True if command sent successfully

    Note:
        Exact behavior depends on Traktor mapping.
        May need value adjustment (127, 126, etc.)
    """
    items = max(1, min(63, items))

    # For multiple items, scroll one at a time with delay
    if items > 1 and delay_sec > 0:
        success = True
        for i in range(items):
            # Experimental: Use high values for scroll up
            value = 127 - 1 + 1
            value = max(64, min(127, value))
            if not scroll_list(value):
                success = False
                break
            if i < items - 1:  # Don't delay after last scroll
                time.sleep(delay_sec)
        return success
    else:
        # Experimental: Use high values for scroll up
        value = 127 - items + 1
        value = max(64, min(127, value))
        return scroll_list(value)


def navigate_tree_down() -> bool:
    """
    Navigate down in folder tree structure

    Returns:
        True if command sent successfully

    Example:
        >>> navigate_tree_down()  # Move to next folder in tree
    """
    success = send_midi_cc(BrowserCC.TREE_NAVIGATE_DOWN, 127)

    if success:
        logger.info("Browser tree navigated down")

    return success


def navigate_tree_up() -> bool:
    """
    Navigate up in folder tree structure

    Returns:
        True if command sent successfully

    Example:
        >>> navigate_tree_up()  # Move to previous folder in tree
    """
    success = send_midi_cc(BrowserCC.TREE_NAVIGATE_UP, 127)

    if success:
        logger.info("Browser tree navigated up")

    return success


def toggle_folder_expansion() -> bool:
    """
    Expand or collapse currently selected folder

    Returns:
        True if command sent successfully

    Example:
        >>> toggle_folder_expansion()  # Open closed folder or close open folder
    """
    success = send_midi_cc(BrowserCC.EXPAND_COLLAPSE, 127)

    if success:
        logger.info("Browser folder toggled (expand/collapse)")

    return success


def navigate_to_folder(folder_path: List[str], delay_sec: float = 1.5) -> bool:
    """
    Navigate to specific folder using folder path

    IMPORTANT: Traktor requires time to process navigation commands.
    Default delay is 1.5 seconds between commands.

    Args:
        folder_path: List of folder names from root to target
                    Example: ['Music', 'Techno', 'Berlin']
        delay_sec: Delay between navigation commands (default: 1.5s)

    Returns:
        True if all commands sent successfully

    Note:
        Requires integration with music-vision-navigator for visual confirmation.
        Current implementation is "blind" navigation.

    Example:
        >>> navigate_to_folder(['Music', 'Techno'])
        >>> navigate_to_folder(['Music', 'Techno'], delay_sec=2.0)
    """
    logger.info(f"Navigating to folder: {' > '.join(folder_path)}")

    # This is a placeholder implementation
    # Production version should use visual feedback
    for i, folder in enumerate(folder_path):
        logger.debug(f"  Step {i+1}: {folder}")

        # Navigate down to next level
        if i > 0:
            navigate_tree_down()
            time.sleep(delay_sec)

        # Expand folder
        toggle_folder_expansion()
        time.sleep(delay_sec)

    return True


def scroll_to_track(track_name: str, max_scrolls: int = 50, delay_sec: float = 1.5) -> bool:
    """
    Scroll to specific track by name

    IMPORTANT: Traktor requires time to process each scroll command.
    Default delay is 1.5 seconds per scroll step.

    Args:
        track_name: Track name to find
        max_scrolls: Maximum scroll attempts before giving up
        delay_sec: Delay between scroll steps (default: 1.5s)

    Returns:
        True if track found (requires visual verification)

    Note:
        Requires integration with music-vision-navigator for track name recognition.
        Current implementation is "blind" scrolling.

    Example:
        >>> scroll_to_track("Dynamics - Whole Lotta Love")
        >>> scroll_to_track("Track Name", delay_sec=2.0)
    """
    logger.info(f"Searching for track: {track_name} (max {max_scrolls} scrolls)")

    # This is a placeholder implementation
    # Production version should use OCR/visual feedback
    for i in range(max_scrolls):
        logger.debug(f"  Scroll {i+1}/{max_scrolls}")

        # Use scroll_down with built-in delay
        scroll_down(1, delay_sec=delay_sec)

        # TODO: Add visual verification here
        # if track_visible(track_name):
        #     logger.info(f"Track found after {i+1} scrolls")
        #     return True

    logger.warning(f"Track not found after {max_scrolls} scrolls")
    return False


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_browser_navigator():
    """
    Initialize browser navigator module

    - Initialize MIDI driver
    - Log module status
    """
    logger.info("Initializing browser navigator module")

    # Initialize MIDI driver (ensures connection on startup)
    try:
        get_midi_driver()
    except Exception as e:
        logger.error(f"Failed to initialize MIDI driver: {str(e)}")
        raise

    logger.info("Browser navigator module initialized")


# ============================================================================
# MAIN ENTRY POINT (For Testing)
# ============================================================================

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("BROWSER NAVIGATOR MODULE - TEST")
    print("=" * 60)

    # Initialize
    initialize_browser_navigator()

    # Test commands
    print("\nTesting browser navigation commands...")
    print("(Watch Traktor browser window)")

    print("\n1. Scroll down 1 item...")
    scroll_down(1)
    time.sleep(1)

    print("2. Scroll down 5 items...")
    scroll_down(5)
    time.sleep(1)

    print("3. Navigate tree down...")
    navigate_tree_down()
    time.sleep(1)

    print("4. Navigate tree up...")
    navigate_tree_up()
    time.sleep(1)

    print("5. Toggle folder expansion...")
    toggle_folder_expansion()

    print("\n" + "=" * 60)
    print("BROWSER NAVIGATOR MODULE READY")
    print("=" * 60)
