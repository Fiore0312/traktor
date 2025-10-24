#!/usr/bin/env python3
"""
Browser Navigator Module - Keyboard Shortcuts Version
=====================================================

Provides programmatic control of Traktor's browser using keyboard shortcuts.

**SIMPLIFIED VERSION - No MIDI required!**

Features:
- Track list scrolling (Up/Down arrows)
- Folder tree navigation (Left/Right arrows)
- Track loading to decks (Shift+Left/Right)
- Search functionality (Ctrl+F)

Advantages over MIDI version:
- No loopMIDI, ASIO4ALL, or .tsi mapping needed
- Instant response (no MIDI latency)
- Works on all platforms
- Easy to debug (you can test shortcuts manually)

Author: AI DJ System - Keyboard Migration
Date: 2025-10-22
Version: 2.0.0 (Keyboard Shortcuts)

Based on: browser_navigator.py v1.0.0 (MIDI version)
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from traktor_keyboard_driver import TraktorKeyboardDriver, DeckID

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# GLOBAL STATE
# ============================================================================

# Keyboard driver instance (module-level singleton)
_keyboard_driver = None


def get_keyboard_driver() -> TraktorKeyboardDriver:
    """
    Get or create keyboard driver instance (singleton pattern)

    Returns:
        TraktorKeyboardDriver instance
    """
    global _keyboard_driver
    if _keyboard_driver is None:
        _keyboard_driver = TraktorKeyboardDriver()
        logger.info("TraktorKeyboardDriver initialized for browser navigation")
    return _keyboard_driver


# ============================================================================
# BROWSER NAVIGATION - KEYBOARD SHORTCUTS
# ============================================================================

def scroll_track_list_down(steps: int = 1, delay_seconds: float = 0.1) -> bool:
    """
    Scroll down in browser track list using Down Arrow key.

    Args:
        steps: Number of steps to scroll (default 1)
        delay_seconds: Delay between steps (default 0.1s)

    Returns:
        True if successful
    """
    try:
        driver = get_keyboard_driver()
        driver.browser_scroll_down(steps)
        time.sleep(delay_seconds)
        logger.info(f"Browser scrolled down {steps} steps")
        return True
    except Exception as e:
        logger.error(f"Failed to scroll browser down: {e}")
        return False


def scroll_track_list_up(steps: int = 1, delay_seconds: float = 0.1) -> bool:
    """
    Scroll up in browser track list using Up Arrow key.

    Args:
        steps: Number of steps to scroll (default 1)
        delay_seconds: Delay between steps (default 0.1s)

    Returns:
        True if successful
    """
    try:
        driver = get_keyboard_driver()
        driver.browser_scroll_up(steps)
        time.sleep(delay_seconds)
        logger.info(f"Browser scrolled up {steps} steps")
        return True
    except Exception as e:
        logger.error(f"Failed to scroll browser up: {e}")
        return False


def navigate_folder_tree_right(steps: int = 1, delay_seconds: float = 0.1) -> bool:
    """
    Navigate right in folder tree (expand folder or go deeper).

    Uses Right Arrow key.

    Args:
        steps: Number of steps to navigate (default 1)
        delay_seconds: Delay between steps (default 0.1s)

    Returns:
        True if successful
    """
    try:
        driver = get_keyboard_driver()
        driver.browser_tree_right(steps)
        time.sleep(delay_seconds)
        logger.info(f"Browser tree navigated right {steps} steps")
        return True
    except Exception as e:
        logger.error(f"Failed to navigate tree right: {e}")
        return False


def navigate_folder_tree_left(steps: int = 1, delay_seconds: float = 0.1) -> bool:
    """
    Navigate left in folder tree (collapse folder or go up).

    Uses Left Arrow key.

    Args:
        steps: Number of steps to navigate (default 1)
        delay_seconds: Delay between steps (default 0.1s)

    Returns:
        True if successful
    """
    try:
        driver = get_keyboard_driver()
        driver.browser_tree_left(steps)
        time.sleep(delay_seconds)
        logger.info(f"Browser tree navigated left {steps} steps")
        return True
    except Exception as e:
        logger.error(f"Failed to navigate tree left: {e}")
        return False


def load_selected_to_deck(deck: str) -> bool:
    """
    Load currently selected track to specified deck.

    Args:
        deck: Deck ID ('A' or 'B')

    Returns:
        True if successful
    """
    try:
        driver = get_keyboard_driver()
        deck_id = DeckID.A if deck.upper() == 'A' else DeckID.B
        driver.load_selected_track(deck_id)
        logger.info(f"Track loaded to Deck {deck}")
        return True
    except Exception as e:
        logger.error(f"Failed to load track to Deck {deck}: {e}")
        return False


def search_browser(query: str, delay_seconds: float = 0.3) -> bool:
    """
    Search browser using Ctrl+F and type query.

    Args:
        query: Search query to type
        delay_seconds: Delay after search (default 0.3s)

    Returns:
        True if successful
    """
    try:
        driver = get_keyboard_driver()
        driver.browser_search(query)
        time.sleep(delay_seconds)
        logger.info(f"Browser searched for: '{query}'")
        return True
    except Exception as e:
        logger.error(f"Failed to search browser: {e}")
        return False


# ============================================================================
# HIGH-LEVEL NAVIGATION WORKFLOWS
# ============================================================================

def navigate_to_position(
    target_position: int,
    current_position: int = 1,
    delay_between_steps: float = 0.1
) -> bool:
    """
    Navigate browser to target position from current position.

    SIMPLIFIED: Just uses Up/Down arrow keys, no timing compensation needed.

    Args:
        target_position: Target position (1-based)
        current_position: Current position (1-based, default 1)
        delay_between_steps: Delay between navigation steps

    Returns:
        True if successful
    """
    steps_needed = target_position - current_position

    if steps_needed == 0:
        logger.info("Already at target position")
        return True

    if steps_needed > 0:
        # Navigate down
        logger.info(f"Navigating down {steps_needed} steps to position {target_position}")
        return scroll_track_list_down(steps_needed, delay_between_steps)
    else:
        # Navigate up
        steps_up = abs(steps_needed)
        logger.info(f"Navigating up {steps_up} steps to position {target_position}")
        return scroll_track_list_up(steps_up, delay_between_steps)


def navigate_to_folder_and_load(
    folder_name: str,
    track_position: int = 1,
    deck: str = 'A'
) -> bool:
    """
    Complete workflow: search for folder, navigate to track, load to deck.

    Args:
        folder_name: Folder name to search for
        track_position: Position in folder (1-based)
        deck: Deck to load to ('A' or 'B')

    Returns:
        True if successful
    """
    logger.info(
        f"Starting navigation workflow: folder='{folder_name}', "
        f"track_position={track_position}, deck={deck}"
    )

    try:
        # Step 1: Search for folder
        if not search_browser(folder_name):
            return False
        time.sleep(0.3)

        # Step 2: Press Enter to select first result
        import pyautogui
        pyautogui.press('enter')
        time.sleep(0.2)

        # Step 3: Navigate to track position
        if track_position > 1:
            if not scroll_track_list_down(track_position - 1):
                return False
            time.sleep(0.2)

        # Step 4: Load to deck
        if not load_selected_to_deck(deck):
            return False

        logger.info(
            f"Navigation workflow completed: '{folder_name}' position {track_position} "
            f"loaded to Deck {deck}"
        )
        return True

    except Exception as e:
        logger.error(f"Navigation workflow failed: {e}")
        return False


# ============================================================================
# COMPLETE AUTONOMOUS WORKFLOW (KEYBOARD VERSION)
# ============================================================================

def autonomous_track_selection_keyboard(
    folder_name: str,
    track_position: int,
    deck: str,
    set_master: bool = False,
    enable_sync: bool = False
) -> bool:
    """
    Complete autonomous workflow using ONLY keyboard shortcuts.

    Workflow:
    1. Search for folder by name
    2. Navigate to track position
    3. Load track to deck
    4. Configure deck (MASTER/SYNC)
    5. Start playback

    Args:
        folder_name: Folder to navigate to
        track_position: Track position in folder (1-based)
        deck: Deck to load to ('A' or 'B')
        set_master: Whether to set deck as tempo master
        enable_sync: Whether to enable SYNC

    Returns:
        True if successful
    """
    logger.info(
        f"Starting autonomous track selection (keyboard): "
        f"folder='{folder_name}', position={track_position}, deck={deck}"
    )

    try:
        # Step 1-4: Navigate and load
        if not navigate_to_folder_and_load(folder_name, track_position, deck):
            return False

        time.sleep(0.5)  # Wait for track to load

        driver = get_keyboard_driver()
        deck_id = DeckID.A if deck.upper() == 'A' else DeckID.B

        # Step 5: Configure deck
        if set_master:
            driver.set_tempo_master(deck_id)
            logger.info(f"Deck {deck} set as TEMPO MASTER")
            time.sleep(0.1)

        if enable_sync:
            driver.sync_on(deck_id)
            logger.info(f"Deck {deck} SYNC enabled")
            time.sleep(0.1)

        # Step 6: Start playback
        driver.play_pause(deck_id)
        logger.info(f"Playback started on Deck {deck}")

        logger.info("Autonomous track selection completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Autonomous track selection failed: {e}")
        return False


# ============================================================================
# TESTING & CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(
        description="Traktor Browser Navigator - Keyboard Shortcuts Version"
    )
    parser.add_argument(
        '--folder',
        type=str,
        help='Folder name to navigate to',
        default='Dub'
    )
    parser.add_argument(
        '--position',
        type=int,
        help='Track position in folder (1-based)',
        default=1
    )
    parser.add_argument(
        '--deck',
        type=str,
        choices=['A', 'B'],
        help='Deck to load to',
        default='A'
    )
    parser.add_argument(
        '--master',
        action='store_true',
        help='Set deck as tempo master'
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Enable SYNC on deck'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run quick test (no autonomous workflow)'
    )

    args = parser.parse_args()

    print("="*70)
    print("Traktor Browser Navigator - Keyboard Shortcuts Version")
    print("="*70)
    print("\nNO MIDI SETUP REQUIRED!")
    print("Just make sure Traktor is running and focused.")
    print("\nStarting in 3 seconds...")
    time.sleep(3)

    if args.test:
        # Quick test mode
        print("\nRunning quick test...")
        print("1. Scrolling down 3 steps...")
        scroll_track_list_down(3)
        time.sleep(1)

        print("2. Scrolling up 3 steps...")
        scroll_track_list_up(3)
        time.sleep(1)

        print("3. Navigate tree right...")
        navigate_folder_tree_right(1)
        time.sleep(1)

        print("4. Navigate tree left...")
        navigate_folder_tree_left(1)

        print("\nTest completed!")

    else:
        # Full autonomous workflow
        success = autonomous_track_selection_keyboard(
            folder_name=args.folder,
            track_position=args.position,
            deck=args.deck,
            set_master=args.master,
            enable_sync=args.sync
        )

        if success:
            print(f"\n✅ SUCCESS: Track loaded and playing on Deck {args.deck}")
        else:
            print("\n❌ FAILED: Check logs for details")
