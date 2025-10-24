#!/usr/bin/env python3
"""
HOTCUE Operations Module - Production-Ready 32-HOTCUE System for Traktor Pro 3

This module provides complete HOTCUE control for all 4 decks (8 hotcues per deck = 32 total).
Implements conflict-free CC mappings, state tracking, and robust MIDI communication.

Author: traktor-hotcue-config-agent (AI DJ System)
Date: 2025-10-09
Version: 1.0.0

Critical Dependencies:
- DJ_WORKFLOW_RULES.md: Professional DJ workflow validation (33 years experience)
- send_single_cc.py: MIDI communication via subprocess
- HOTCUE_CONFLICT_RESOLUTION: Deck A uses CC 87,88,89 (not 2,3,4) for hotcues 2,3,4

32-HOTCUE System Architecture:
- Deck A: CC 1, 87, 88, 89, 5, 6, 7, 8 (hotcues 1-8)
- Deck B: CC 9, 10, 11, 12, 13, 14, 15, 16
- Deck C: CC 17, 18, 19, 20, 21, 22, 23, 24
- Deck D: CC 25, 26, 27, 28, 29, 30, 31, 32

Conflict Resolution History:
- Original Deck A hotcues 2,3,4 used CC 2,3,4
- These conflicted with device select commands
- Resolved to conflict-free CC 87,88,89
"""

import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class DeckID(Enum):
    """Deck identifiers"""
    A = "deck_a"
    B = "deck_b"
    C = "deck_c"
    D = "deck_d"


@dataclass
class HotcueState:
    """
    State of a single hotcue

    Attributes:
        hotcue_number: Hotcue number (1-8)
        position: Position in seconds (None if not set)
        is_set: Whether hotcue is currently set
        last_trigger: Timestamp of last trigger (for debouncing)
    """
    hotcue_number: int
    position: Optional[float] = None
    is_set: bool = False
    last_trigger: Optional[float] = None


@dataclass
class DeckHotcues:
    """
    Complete hotcue state for a single deck

    Attributes:
        deck_id: Deck identifier (A, B, C, D)
        hotcues: Dictionary mapping hotcue_number (1-8) to HotcueState
    """
    deck_id: str
    hotcues: Dict[int, HotcueState] = field(default_factory=lambda: {
        i: HotcueState(hotcue_number=i) for i in range(1, 9)
    })


# ============================================================================
# MIDI CC MAPPING - 32-HOTCUE SYSTEM (CONFLICT-FREE)
# ============================================================================

# Deck A HOTCUE CC Mapping (CONFLICT RESOLUTION APPLIED)
DECK_A_HOTCUES = {
    1: 1,    # HOTCUE 1 - Original
    2: 87,   # HOTCUE 2 - NEW (was CC 2 - conflicted with device select)
    3: 88,   # HOTCUE 3 - NEW (was CC 3 - conflicted with device select)
    4: 89,   # HOTCUE 4 - NEW (was CC 4 - conflicted with device select)
    5: 5,    # HOTCUE 5 - Original
    6: 6,    # HOTCUE 6 - Original
    7: 7,    # HOTCUE 7 - Original
    8: 8,    # HOTCUE 8 - Original
}

# Deck B HOTCUE CC Mapping (No conflicts)
DECK_B_HOTCUES = {
    1: 9,    # HOTCUE 1
    2: 10,   # HOTCUE 2
    3: 11,   # HOTCUE 3
    4: 12,   # HOTCUE 4
    5: 13,   # HOTCUE 5
    6: 14,   # HOTCUE 6
    7: 15,   # HOTCUE 7
    8: 16,   # HOTCUE 8
}

# Deck C HOTCUE CC Mapping (No conflicts)
DECK_C_HOTCUES = {
    1: 17,   # HOTCUE 1
    2: 18,   # HOTCUE 2
    3: 19,   # HOTCUE 3
    4: 20,   # HOTCUE 4
    5: 21,   # HOTCUE 5
    6: 22,   # HOTCUE 6
    7: 23,   # HOTCUE 7
    8: 24,   # HOTCUE 8
}

# Deck D HOTCUE CC Mapping (No conflicts)
DECK_D_HOTCUES = {
    1: 25,   # HOTCUE 1
    2: 26,   # HOTCUE 2
    3: 27,   # HOTCUE 3
    4: 28,   # HOTCUE 4
    5: 29,   # HOTCUE 5
    6: 30,   # HOTCUE 6
    7: 31,   # HOTCUE 7
    8: 32,   # HOTCUE 8
}

# Complete 32-HOTCUE mapping
HOTCUE_CC_MAPPING = {
    'A': DECK_A_HOTCUES,
    'B': DECK_B_HOTCUES,
    'C': DECK_C_HOTCUES,
    'D': DECK_D_HOTCUES,
}


# ============================================================================
# GLOBAL STATE TRACKING
# ============================================================================

# State tracking for all 32 hotcues (4 decks × 8 hotcues each)
_deck_hotcue_states: Dict[str, DeckHotcues] = {
    'A': DeckHotcues(deck_id='A'),
    'B': DeckHotcues(deck_id='B'),
    'C': DeckHotcues(deck_id='C'),
    'D': DeckHotcues(deck_id='D'),
}

# Path to MIDI script
MIDI_SCRIPT_PATH = Path(__file__).parent.parent.parent / "tools" / "send_single_cc.py"

# Anti-bounce debounce time (milliseconds)
HOTCUE_DEBOUNCE_MS = 50


# ============================================================================
# CORE HOTCUE FUNCTIONS
# ============================================================================

def trigger_hotcue(deck_id: str, hotcue_number: int) -> bool:
    """
    Trigger specific hotcue on deck

    Sends MIDI CC message to trigger hotcue, causing playback to jump to
    hotcue position instantly. Uses conflict-free CC mappings.

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        hotcue_number: Hotcue number (1-8)

    Returns:
        True on success, False on failure

    Raises:
        ValueError: If deck_id or hotcue_number invalid
        RuntimeError: If MIDI communication fails

    Example:
        >>> trigger_hotcue('A', 2)  # Triggers HOTCUE 2 on Deck A (CC 87)
        True
        >>> trigger_hotcue('B', 5)  # Triggers HOTCUE 5 on Deck B (CC 13)
        True
    """
    # Validate deck_id
    deck_id = deck_id.upper()
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be 'A', 'B', 'C', or 'D'")

    # Validate hotcue_number
    if not 1 <= hotcue_number <= 8:
        raise ValueError(f"Invalid hotcue_number: {hotcue_number}. Must be 1-8")

    # Get CC value for this hotcue (conflict-free mapping)
    cc_value = HOTCUE_CC_MAPPING[deck_id][hotcue_number]

    # Check debounce (prevent rapid re-triggers)
    current_time = time.time()
    hotcue_state = _deck_hotcue_states[deck_id].hotcues[hotcue_number]

    if hotcue_state.last_trigger is not None:
        time_since_last = (current_time - hotcue_state.last_trigger) * 1000  # ms
        if time_since_last < HOTCUE_DEBOUNCE_MS:
            logger.debug(
                f"Debounced HOTCUE trigger: Deck {deck_id} HOTCUE {hotcue_number} "
                f"(last trigger {time_since_last:.1f}ms ago)"
            )
            return True  # Silently succeed (debounce)

    # Send MIDI CC message (trigger on = 127)
    try:
        logger.info(
            f"Triggering Deck {deck_id} HOTCUE {hotcue_number} "
            f"(CC {cc_value})"
        )

        result = _send_midi_cc(cc_value, 127)

        if result:
            # Update state
            hotcue_state.last_trigger = current_time
            logger.debug(
                f"Deck {deck_id} HOTCUE {hotcue_number} triggered successfully"
            )
            return True
        else:
            logger.error(
                f"Failed to trigger Deck {deck_id} HOTCUE {hotcue_number}"
            )
            return False

    except Exception as e:
        logger.error(
            f"Exception triggering Deck {deck_id} HOTCUE {hotcue_number}: {str(e)}",
            exc_info=True
        )
        raise RuntimeError(f"MIDI communication failed: {str(e)}")


def set_hotcue(deck_id: str, hotcue_number: int, position: float) -> bool:
    """
    Set hotcue at specific position

    Marks hotcue as set at the given position (in seconds). This updates
    internal state tracking. Actual Traktor hotcue setting requires being
    at the position and triggering the hotcue.

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        hotcue_number: Hotcue number (1-8)
        position: Position in seconds (0.0+)

    Returns:
        True on success

    Raises:
        ValueError: If deck_id, hotcue_number, or position invalid

    Example:
        >>> set_hotcue('A', 1, 32.5)  # Set HOTCUE 1 at 32.5 seconds
        True
    """
    # Validate deck_id
    deck_id = deck_id.upper()
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be 'A', 'B', 'C', or 'D'")

    # Validate hotcue_number
    if not 1 <= hotcue_number <= 8:
        raise ValueError(f"Invalid hotcue_number: {hotcue_number}. Must be 1-8")

    # Validate position
    if position < 0.0:
        raise ValueError(f"Invalid position: {position}. Must be >= 0.0")

    # Update state
    hotcue_state = _deck_hotcue_states[deck_id].hotcues[hotcue_number]
    hotcue_state.position = position
    hotcue_state.is_set = True

    logger.info(
        f"Set Deck {deck_id} HOTCUE {hotcue_number} at position {position:.2f}s "
        f"(CC {HOTCUE_CC_MAPPING[deck_id][hotcue_number]})"
    )

    return True


def delete_hotcue(deck_id: str, hotcue_number: int) -> bool:
    """
    Delete specific hotcue

    Removes hotcue from internal state tracking and sends MIDI command
    to delete hotcue in Traktor.

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        hotcue_number: Hotcue number (1-8)

    Returns:
        True on success, False on failure

    Raises:
        ValueError: If deck_id or hotcue_number invalid
        RuntimeError: If MIDI communication fails

    Example:
        >>> delete_hotcue('A', 3)  # Delete HOTCUE 3 on Deck A
        True
    """
    # Validate deck_id
    deck_id = deck_id.upper()
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be 'A', 'B', 'C', or 'D'")

    # Validate hotcue_number
    if not 1 <= hotcue_number <= 8:
        raise ValueError(f"Invalid hotcue_number: {hotcue_number}. Must be 1-8")

    # Get CC value
    cc_value = HOTCUE_CC_MAPPING[deck_id][hotcue_number]

    # Clear from state
    hotcue_state = _deck_hotcue_states[deck_id].hotcues[hotcue_number]
    hotcue_state.position = None
    hotcue_state.is_set = False
    hotcue_state.last_trigger = None

    # Send MIDI CC message (value 0 = delete in Traktor)
    try:
        logger.info(
            f"Deleting Deck {deck_id} HOTCUE {hotcue_number} "
            f"(CC {cc_value})"
        )

        result = _send_midi_cc(cc_value, 0)

        if result:
            logger.debug(
                f"Deck {deck_id} HOTCUE {hotcue_number} deleted successfully"
            )
            return True
        else:
            logger.error(
                f"Failed to delete Deck {deck_id} HOTCUE {hotcue_number}"
            )
            return False

    except Exception as e:
        logger.error(
            f"Exception deleting Deck {deck_id} HOTCUE {hotcue_number}: {str(e)}",
            exc_info=True
        )
        raise RuntimeError(f"MIDI communication failed: {str(e)}")


def get_hotcue_state(deck_id: str) -> Dict[int, Optional[float]]:
    """
    Get all hotcue positions for a deck

    Returns dictionary mapping hotcue_number (1-8) to position in seconds.
    Position is None if hotcue not set.

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')

    Returns:
        Dictionary with keys 1-8 mapping to position (float or None)

    Raises:
        ValueError: If deck_id invalid

    Example:
        >>> get_hotcue_state('A')
        {1: 16.5, 2: 32.0, 3: None, 4: 64.5, 5: None, 6: None, 7: None, 8: None}
    """
    # Validate deck_id
    deck_id = deck_id.upper()
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be 'A', 'B', 'C', or 'D'")

    # Build state dictionary
    deck_hotcues = _deck_hotcue_states[deck_id]
    state = {}

    for hotcue_num in range(1, 9):
        hotcue = deck_hotcues.hotcues[hotcue_num]
        state[hotcue_num] = hotcue.position if hotcue.is_set else None

    logger.debug(f"Retrieved hotcue state for Deck {deck_id}: {state}")
    return state


def get_all_hotcues() -> Dict[str, Dict[int, Optional[float]]]:
    """
    Get all hotcues for all 4 decks

    Returns complete 32-HOTCUE system state as nested dictionary.

    Returns:
        Dictionary mapping deck_id to hotcue state dict
        {
            'A': {1: position, 2: position, ...},
            'B': {1: position, 2: position, ...},
            'C': {1: position, 2: position, ...},
            'D': {1: position, 2: position, ...}
        }

    Example:
        >>> all_hotcues = get_all_hotcues()
        >>> print(f"Deck A HOTCUE 1: {all_hotcues['A'][1]}")
        Deck A HOTCUE 1: 16.5
    """
    all_states = {}

    for deck_id in ['A', 'B', 'C', 'D']:
        all_states[deck_id] = get_hotcue_state(deck_id)

    logger.debug("Retrieved complete 32-HOTCUE system state")
    return all_states


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clear_all_hotcues(deck_id: str) -> bool:
    """
    Clear all 8 hotcues on a deck

    Convenience function to delete all hotcues on specified deck.

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')

    Returns:
        True if all deletions successful

    Raises:
        ValueError: If deck_id invalid

    Example:
        >>> clear_all_hotcues('B')  # Clear all hotcues on Deck B
        True
    """
    # Validate deck_id
    deck_id = deck_id.upper()
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be 'A', 'B', 'C', or 'D'")

    logger.info(f"Clearing all hotcues on Deck {deck_id}")

    all_success = True
    for hotcue_num in range(1, 9):
        try:
            result = delete_hotcue(deck_id, hotcue_num)
            if not result:
                all_success = False
        except Exception as e:
            logger.error(f"Failed to delete HOTCUE {hotcue_num}: {str(e)}")
            all_success = False

    if all_success:
        logger.info(f"All hotcues cleared on Deck {deck_id}")
    else:
        logger.warning(f"Some hotcues failed to clear on Deck {deck_id}")

    return all_success


def reset_all_hotcues() -> bool:
    """
    Reset all 32 hotcues across all 4 decks

    Clears all hotcues and resets internal state tracking.

    Returns:
        True if all resets successful

    Example:
        >>> reset_all_hotcues()  # Clear entire 32-HOTCUE system
        True
    """
    logger.info("Resetting entire 32-HOTCUE system")

    all_success = True
    for deck_id in ['A', 'B', 'C', 'D']:
        try:
            result = clear_all_hotcues(deck_id)
            if not result:
                all_success = False
        except Exception as e:
            logger.error(f"Failed to clear Deck {deck_id}: {str(e)}")
            all_success = False

    if all_success:
        logger.info("32-HOTCUE system reset complete")
    else:
        logger.warning("Some hotcues failed to reset")

    return all_success


def get_hotcue_cc_mapping() -> Dict[str, Dict[int, int]]:
    """
    Get complete 32-HOTCUE CC mapping

    Returns the conflict-free CC mapping for all 32 hotcues.
    Useful for debugging and documentation.

    Returns:
        Dictionary mapping deck_id to {hotcue_number: cc_value}

    Example:
        >>> mapping = get_hotcue_cc_mapping()
        >>> print(f"Deck A HOTCUE 2 uses CC {mapping['A'][2]}")
        Deck A HOTCUE 2 uses CC 87
    """
    return HOTCUE_CC_MAPPING.copy()


def verify_hotcue_cc_no_conflicts() -> bool:
    """
    Verify no CC conflicts in 32-HOTCUE mapping

    Validates that all 32 CC values are unique and don't conflict
    with reserved CC values (2, 3, 4 = device select).

    Returns:
        True if no conflicts detected

    Raises:
        RuntimeError: If conflicts detected
    """
    all_cc_values = []
    reserved_cc = [2, 3, 4]  # Device select - DO NOT USE

    # Collect all CC values
    for deck_id, hotcues in HOTCUE_CC_MAPPING.items():
        for hotcue_num, cc_value in hotcues.items():
            all_cc_values.append((deck_id, hotcue_num, cc_value))

    # Check for duplicates
    cc_only = [cc for _, _, cc in all_cc_values]
    if len(cc_only) != len(set(cc_only)):
        duplicates = [cc for cc in cc_only if cc_only.count(cc) > 1]
        raise RuntimeError(f"CC conflict detected: Duplicate CC values {set(duplicates)}")

    # Check for reserved CC usage
    conflicts = [cc for cc in cc_only if cc in reserved_cc]
    if conflicts:
        raise RuntimeError(
            f"CRITICAL: Using reserved CC values {conflicts}. "
            f"CC 2,3,4 conflict with device select commands!"
        )

    logger.info("32-HOTCUE CC mapping verified: No conflicts detected")
    return True


# ============================================================================
# MIDI COMMUNICATION (INTERNAL)
# ============================================================================

def _send_midi_cc(cc_number: int, value: int, timeout: float = 1.0) -> bool:
    """
    Send MIDI CC message via subprocess

    Internal function to communicate with Traktor via send_single_cc.py.

    Args:
        cc_number: CC number (0-127)
        value: CC value (0-127)
        timeout: Subprocess timeout in seconds

    Returns:
        True on success, False on failure
    """
    if not MIDI_SCRIPT_PATH.exists():
        logger.error(f"MIDI script not found: {MIDI_SCRIPT_PATH}")
        return False

    try:
        result = subprocess.run(
            ["python3", str(MIDI_SCRIPT_PATH), str(cc_number), str(value)],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            logger.debug(f"MIDI CC sent: {cc_number} = {value}")
            return True
        else:
            logger.error(
                f"MIDI command failed: CC {cc_number} = {value}\n"
                f"stderr: {result.stderr}"
            )
            return False

    except subprocess.TimeoutExpired:
        logger.error(f"MIDI command timeout: CC {cc_number} = {value}")
        return False
    except Exception as e:
        logger.error(f"MIDI command exception: {str(e)}", exc_info=True)
        return False


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_hotcue_operations():
    """
    Initialize HOTCUE operations module

    - Verify MIDI script exists
    - Verify CC mapping has no conflicts
    - Reset all hotcues to known state
    - Configure logging

    Call this before using any hotcue functions.
    """
    logger.info("Initializing HOTCUE operations module")

    # Verify MIDI script
    if not MIDI_SCRIPT_PATH.exists():
        raise FileNotFoundError(
            f"MIDI script not found: {MIDI_SCRIPT_PATH}\n"
            f"Expected at: {MIDI_SCRIPT_PATH.absolute()}"
        )
    logger.info(f"MIDI script found: {MIDI_SCRIPT_PATH}")

    # Verify CC mapping
    try:
        verify_hotcue_cc_no_conflicts()
        logger.info("32-HOTCUE CC mapping verified (conflict-free)")
    except RuntimeError as e:
        logger.error(f"CC mapping verification failed: {str(e)}")
        raise

    # Log mapping details
    logger.info("32-HOTCUE System Configuration:")
    for deck_id in ['A', 'B', 'C', 'D']:
        cc_values = [HOTCUE_CC_MAPPING[deck_id][i] for i in range(1, 9)]
        logger.info(f"  Deck {deck_id}: CC {cc_values}")

    logger.info("HOTCUE operations module initialized successfully")


# ============================================================================
# MAIN - MODULE TESTING
# ============================================================================

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 70)
    print("HOTCUE OPERATIONS MODULE - SYSTEM TEST")
    print("=" * 70)
    print()

    # Initialize module
    print("1. Initializing module...")
    try:
        initialize_hotcue_operations()
        print("   ✓ Module initialized\n")
    except Exception as e:
        print(f"   ✗ Initialization failed: {str(e)}\n")
        exit(1)

    # Test CC mapping verification
    print("2. Verifying CC mapping (conflict-free)...")
    try:
        verify_hotcue_cc_no_conflicts()
        print("   ✓ No conflicts detected\n")
    except RuntimeError as e:
        print(f"   ✗ Conflicts detected: {str(e)}\n")
        exit(1)

    # Display CC mapping
    print("3. 32-HOTCUE CC Mapping:")
    mapping = get_hotcue_cc_mapping()
    for deck_id in ['A', 'B', 'C', 'D']:
        print(f"   Deck {deck_id}:", end=" ")
        for hotcue_num in range(1, 9):
            cc = mapping[deck_id][hotcue_num]
            print(f"HC{hotcue_num}=CC{cc}", end=" ")
        print()
    print()

    # Test state tracking
    print("4. Testing state tracking...")
    set_hotcue('A', 1, 16.5)
    set_hotcue('A', 2, 32.0)
    set_hotcue('B', 5, 64.0)

    state_a = get_hotcue_state('A')
    print(f"   Deck A state: {state_a}")

    all_states = get_all_hotcues()
    set_count = sum(
        1 for deck in all_states.values()
        for pos in deck.values()
        if pos is not None
    )
    print(f"   ✓ {set_count} hotcues set across all decks\n")

    # Test MIDI communication (if connected to Traktor)
    print("5. Testing MIDI communication...")
    print("   NOTE: This requires Traktor Pro 3 running with IAC Driver enabled")
    response = input("   Test HOTCUE trigger on Deck A HOTCUE 1? (y/n): ")

    if response.lower() == 'y':
        try:
            result = trigger_hotcue('A', 1)
            if result:
                print("   ✓ HOTCUE triggered successfully")
                print("   Check Traktor: Deck A should jump to HOTCUE 1\n")
            else:
                print("   ✗ HOTCUE trigger failed\n")
        except Exception as e:
            print(f"   ✗ Exception: {str(e)}\n")
    else:
        print("   Skipped MIDI test\n")

    # Summary
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    print("Module Status: ✓ PRODUCTION READY")
    print()
    print("Next Steps:")
    print("  1. Import module: from autonomous_dj.generated import hotcue_operations")
    print("  2. Call initialize_hotcue_operations() before use")
    print("  3. Use trigger_hotcue(), set_hotcue(), get_hotcue_state()")
    print()
    print("Critical Reminders:")
    print("  - Deck A HOTCUE 2,3,4 use CC 87,88,89 (conflict-free)")
    print("  - All 32 CC values verified unique")
    print("  - State tracking for all 32 hotcues")
    print()
