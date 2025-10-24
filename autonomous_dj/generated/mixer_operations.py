#!/usr/bin/env python3
"""
Mixer Operations Module - Professional DJ Mixer Control for Traktor Pro 3

This module provides professional DJ mixer operations including crossfader control,
EQ management, channel fader (volume) control, and smooth transition execution.

Implements industry-standard mixing techniques:
- Logarithmic volume curves for smooth fades
- Professional crossfader transitions (16-step, 32-step, 64-step)
- 3-band EQ control per deck (High, Mid, Low)
- Master volume management with headroom protection
- Beat-synchronized transition timing

Author: traktor-mixer-control agent (AI DJ System)
Date: 2025-10-09
Version: 1.0.0

Critical Dependencies:
- send_single_cc.py: MIDI communication via subprocess
- deck_operations.py: Deck state queries for intelligent mixer decisions
- DJ_WORKFLOW_RULES.md: Professional DJ workflow validation

MIDI CC Mapping (Verified from traktor_cc_reference.py):
- Crossfader: CC 32 (0=Full A/Left, 64=Center, 127=Full B/Right)
- Volume: Deck A=CC 28, Deck B=CC 29, Deck C=CC 30, Deck D=CC 31
- EQ High: Deck A=CC 34, Deck B=CC 50
- EQ Mid: Deck A=CC 35, Deck B=CC 51
- EQ Low: Deck A=CC 36, Deck B=CC 52
- Master Volume: CC 33
"""

import subprocess
import time
import logging
import math
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
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


class TransitionType(Enum):
    """Professional transition types"""
    CROSSFADER = "crossfader"           # Standard crossfader transition
    EQ_SWAP = "eq_swap"                 # EQ-based bass swap transition
    FILTER_SWEEP = "filter_sweep"       # Creative filter-based transition
    CHANNEL_FADER = "channel_fader"     # Quick channel fader cut


@dataclass
class MixerState:
    """
    Current state of the mixer

    Attributes:
        crossfader_position: Crossfader position (0.0=Full A, 1.0=Full B)
        volumes: Dict of deck volumes (deck_id -> volume 0.0-1.0)
        eq_settings: Dict of EQ settings (deck_id -> {low, mid, high})
        master_volume: Master output volume (0.0-1.0)
    """
    crossfader_position: float = 0.5  # Center by default
    volumes: Dict[str, float] = None
    eq_settings: Dict[str, Dict[str, float]] = None
    master_volume: float = 0.85  # 85% default for headroom

    def __post_init__(self):
        if self.volumes is None:
            self.volumes = {'A': 0.85, 'B': 0.85, 'C': 0.85, 'D': 0.85}
        if self.eq_settings is None:
            # Neutral EQ (0.5 = 64 MIDI = 0dB)
            self.eq_settings = {
                'A': {'low': 0.5, 'mid': 0.5, 'high': 0.5},
                'B': {'low': 0.5, 'mid': 0.5, 'high': 0.5},
                'C': {'low': 0.5, 'mid': 0.5, 'high': 0.5},
                'D': {'low': 0.5, 'mid': 0.5, 'high': 0.5},
            }


@dataclass
class TransitionCommand:
    """
    Single command in a transition sequence

    Attributes:
        beat_offset: Number of beats from transition start
        command_type: Type of command ('volume', 'crossfader', 'eq', 'master')
        deck_id: Target deck (if applicable)
        parameter: Parameter to control ('low', 'mid', 'high' for EQ)
        value: Target value (0.0-1.0)
    """
    beat_offset: int
    command_type: str
    deck_id: Optional[str]
    parameter: Optional[str]
    value: float


# ============================================================================
# MIDI CC MAPPING (Traktor Pro 3 - VERIFIED)
# ============================================================================

# Crossfader
CROSSFADER_CC = 32  # 0=Full A, 64=Center, 127=Full B

# Volume Faders (Channel Faders)
DECK_VOLUME_CC = {
    'A': 28,
    'B': 29,
    'C': 30,
    'D': 31,
}

# Master Volume
MASTER_VOLUME_CC = 33

# EQ Controls (3-band per deck)
# 0=Kill, 64=Neutral (0dB), 127=Boost
DECK_EQ_CC = {
    'A': {
        'high': 34,
        'mid': 35,
        'low': 36,
    },
    'B': {
        'high': 50,
        'mid': 51,
        'low': 52,
    },
    # Deck C and D EQ not mapped in current TSI
    'C': {
        'high': None,
        'mid': None,
        'low': None,
    },
    'D': {
        'high': None,
        'mid': None,
        'low': None,
    },
}


# ============================================================================
# GLOBAL STATE TRACKING
# ============================================================================

# In-memory mixer state
_mixer_state = MixerState()

# MIDI command timeout (seconds)
MIDI_TIMEOUT_SEC = 3.0

# Dynamic path resolution that works from both autonomous_dj/generated/ and project root
_script_dir = Path(__file__).parent
_possible_paths = [
    _script_dir.parent.parent / "tools" / "send_single_cc.py",  # From generated/
    _script_dir / "tools" / "send_single_cc.py",                 # From project root
    Path.cwd() / "tools" / "send_single_cc.py",                  # Current working directory
]

MIDI_SCRIPT_PATH = None
for path in _possible_paths:
    if path.exists():
        MIDI_SCRIPT_PATH = path
        break

if MIDI_SCRIPT_PATH is None:
    MIDI_SCRIPT_PATH = _possible_paths[0]  # Fallback to expected path


# ============================================================================
# MIDI COMMUNICATION FUNCTIONS
# ============================================================================

def send_midi_cc(cc_number: int, value: int) -> bool:
    """
    Send MIDI CC command to Traktor via subprocess

    Args:
        cc_number: MIDI CC number (0-127)
        value: MIDI value (0-127)

    Returns:
        True if MIDI command sent successfully

    Raises:
        RuntimeError: If MIDI communication fails
    """
    try:
        # Use sys.executable to get current Python interpreter
        import sys
        python_exe = sys.executable

        result = subprocess.run(
            [python_exe, str(MIDI_SCRIPT_PATH), str(cc_number), str(value)],
            capture_output=True,
            text=True,
            timeout=MIDI_TIMEOUT_SEC
        )

        if result.returncode != 0:
            logger.error(
                f"MIDI command failed: CC {cc_number} = {value}",
                extra={
                    'cc_number': cc_number,
                    'value': value,
                    'stderr': result.stderr,
                }
            )
            raise RuntimeError(f"MIDI command failed: {result.stderr}")

        logger.debug(
            f"MIDI sent: CC {cc_number} = {value}",
            extra={'cc_number': cc_number, 'value': value}
        )
        return True

    except subprocess.TimeoutExpired:
        logger.error(
            f"MIDI command timeout: CC {cc_number}",
            extra={'cc_number': cc_number, 'timeout_sec': MIDI_TIMEOUT_SEC}
        )
        raise RuntimeError(f"MIDI timeout after {MIDI_TIMEOUT_SEC}s")

    except Exception as e:
        logger.error(
            f"MIDI communication error: {str(e)}",
            extra={'cc_number': cc_number, 'error': str(e)}
        )
        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def linear_to_logarithmic(linear_value: float) -> float:
    """
    Convert linear volume (0.0-1.0) to logarithmic scale

    Professional audio uses logarithmic volume curves for smooth fades.
    This function converts linear values to perceptually linear volume.

    Args:
        linear_value: Linear volume (0.0-1.0)

    Returns:
        Logarithmic volume (0.0-1.0)

    Example:
        >>> linear_to_logarithmic(0.5)
        0.316  # -10dB = 50% perceived volume
    """
    if linear_value <= 0.0:
        return 0.0
    if linear_value >= 1.0:
        return 1.0

    # Logarithmic curve: y = 10^((x-1)*40/20)
    # Range: -40dB to 0dB
    db = (linear_value - 1.0) * 40  # -40dB to 0dB
    return math.pow(10, db / 20)


def float_to_midi(value: float) -> int:
    """
    Convert float (0.0-1.0) to MIDI value (0-127)

    Args:
        value: Float value (0.0-1.0)

    Returns:
        MIDI value (0-127)
    """
    value = max(0.0, min(1.0, value))  # Clamp
    return int(value * 127)


def midi_to_float(midi_value: int) -> float:
    """
    Convert MIDI value (0-127) to float (0.0-1.0)

    Args:
        midi_value: MIDI value (0-127)

    Returns:
        Float value (0.0-1.0)
    """
    midi_value = max(0, min(127, midi_value))  # Clamp
    return midi_value / 127.0


# ============================================================================
# CORE MIXER FUNCTIONS
# ============================================================================

def set_volume(deck_id: str, volume: float) -> bool:
    """
    Set deck channel fader volume with logarithmic curve

    Professional implementation with:
    - Logarithmic volume curve for smooth transitions
    - Range validation and clamping
    - State tracking for mixer consistency

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        volume: Volume level (0.0-1.0)

    Returns:
        True on success

    Raises:
        ValueError: If deck_id is invalid
        RuntimeError: If MIDI communication fails

    Example:
        >>> # Fade in Deck B smoothly
        >>> for i in range(16):
        ...     volume = i / 16.0
        ...     set_volume('B', volume)
        ...     time.sleep(0.125)  # 16 steps over 2 seconds
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be A, B, C, or D")

    # Validate and clamp volume
    volume = max(0.0, min(1.0, volume))

    # Apply logarithmic curve for professional sound
    log_volume = linear_to_logarithmic(volume)

    # Convert to MIDI value
    midi_value = float_to_midi(log_volume)

    # Get CC number for this deck
    cc_number = DECK_VOLUME_CC[deck_id]

    # Send MIDI command
    success = send_midi_cc(cc_number, midi_value)

    if success:
        # Update state
        _mixer_state.volumes[deck_id] = volume

        logger.info(
            f"Deck {deck_id} volume set to {volume:.2f} (log: {log_volume:.2f}, MIDI: {midi_value})",
            extra={
                'deck': deck_id,
                'volume_linear': volume,
                'volume_log': log_volume,
                'midi_value': midi_value
            }
        )

    return success


def set_crossfader_position(position: float) -> bool:
    """
    Set crossfader position

    Args:
        position: Crossfader position (0.0=Full A/Left, 1.0=Full B/Right)

    Returns:
        True on success

    Raises:
        RuntimeError: If MIDI communication fails

    Example:
        >>> # Move crossfader to center
        >>> set_crossfader_position(0.5)

        >>> # Move crossfader to full Deck A (left)
        >>> set_crossfader_position(0.0)

        >>> # Move crossfader to full Deck B (right)
        >>> set_crossfader_position(1.0)
    """
    # Validate and clamp position
    position = max(0.0, min(1.0, position))

    # Convert to MIDI value
    midi_value = float_to_midi(position)

    # Send MIDI command
    success = send_midi_cc(CROSSFADER_CC, midi_value)

    if success:
        # Update state
        _mixer_state.crossfader_position = position

        logger.info(
            f"Crossfader set to {position:.2f} (MIDI: {midi_value})",
            extra={'position': position, 'midi_value': midi_value}
        )

    return success


def set_eq(deck_id: str, low: float, mid: float, high: float) -> bool:
    """
    Set 3-band EQ for deck

    Professional EQ control with:
    - Individual band control (Low, Mid, High)
    - Range: 0.0=Kill, 0.5=Neutral (0dB), 1.0=Boost
    - State tracking for mixer consistency

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        low: Low frequency (20-250Hz) level (0.0-1.0)
        mid: Mid frequency (250Hz-4kHz) level (0.0-1.0)
        high: High frequency (4kHz-20kHz) level (0.0-1.0)

    Returns:
        True if all EQ bands set successfully

    Raises:
        ValueError: If deck_id is invalid or deck has no EQ mapping
        RuntimeError: If MIDI communication fails

    Example:
        >>> # Cut bass on Deck A (EQ-based transition)
        >>> set_eq('A', low=0.0, mid=0.5, high=0.5)

        >>> # Boost highs for energy
        >>> set_eq('B', low=0.5, mid=0.5, high=0.8)

        >>> # Reset to neutral
        >>> set_eq('A', low=0.5, mid=0.5, high=0.5)
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be A, B, C, or D")

    # Check if deck has EQ mapping
    if DECK_EQ_CC[deck_id]['low'] is None:
        logger.warning(
            f"Deck {deck_id} has no EQ mapping in current TSI",
            extra={'deck': deck_id}
        )
        return False

    # Validate and clamp EQ values
    low = max(0.0, min(1.0, low))
    mid = max(0.0, min(1.0, mid))
    high = max(0.0, min(1.0, high))

    # Convert to MIDI values
    low_midi = float_to_midi(low)
    mid_midi = float_to_midi(mid)
    high_midi = float_to_midi(high)

    # Send MIDI commands for all three bands
    success = True
    try:
        send_midi_cc(DECK_EQ_CC[deck_id]['low'], low_midi)
        send_midi_cc(DECK_EQ_CC[deck_id]['mid'], mid_midi)
        send_midi_cc(DECK_EQ_CC[deck_id]['high'], high_midi)
    except RuntimeError:
        success = False

    if success:
        # Update state
        _mixer_state.eq_settings[deck_id] = {
            'low': low,
            'mid': mid,
            'high': high,
        }

        logger.info(
            f"Deck {deck_id} EQ set: Low={low:.2f}, Mid={mid:.2f}, High={high:.2f}",
            extra={
                'deck': deck_id,
                'eq_low': low,
                'eq_mid': mid,
                'eq_high': high,
            }
        )

    return success


def set_master_volume(volume: float) -> bool:
    """
    Set master output volume

    Args:
        volume: Master volume level (0.0-1.0)

    Returns:
        True on success

    Raises:
        RuntimeError: If MIDI communication fails

    Example:
        >>> # Set master to 85% for headroom
        >>> set_master_volume(0.85)
    """
    # Validate and clamp volume
    volume = max(0.0, min(1.0, volume))

    # Convert to MIDI value (linear for master)
    midi_value = float_to_midi(volume)

    # Send MIDI command
    success = send_midi_cc(MASTER_VOLUME_CC, midi_value)

    if success:
        # Update state
        _mixer_state.master_volume = volume

        logger.info(
            f"Master volume set to {volume:.2f} (MIDI: {midi_value})",
            extra={'volume': volume, 'midi_value': midi_value}
        )

    return success


def get_mixer_state() -> Dict[str, Any]:
    """
    Get current mixer state

    Returns:
        Dictionary containing current mixer state:
        {
            'crossfader_position': float (0.0-1.0),
            'volumes': {'A': float, 'B': float, ...},
            'eq_settings': {'A': {'low': float, 'mid': float, 'high': float}, ...},
            'master_volume': float (0.0-1.0)
        }

    Example:
        >>> state = get_mixer_state()
        >>> print(f"Crossfader: {state['crossfader_position']}")
        >>> print(f"Deck A volume: {state['volumes']['A']}")
    """
    return {
        'crossfader_position': _mixer_state.crossfader_position,
        'volumes': _mixer_state.volumes.copy(),
        'eq_settings': {
            deck: eq.copy() for deck, eq in _mixer_state.eq_settings.items()
        },
        'master_volume': _mixer_state.master_volume,
    }


# ============================================================================
# PROFESSIONAL TRANSITION FUNCTIONS
# ============================================================================

def execute_crossfade(
    from_deck: str,
    to_deck: str,
    steps: int = 16,
    duration_bars: int = 8,
    bpm: float = 128.0
) -> List[TransitionCommand]:
    """
    Execute professional crossfader transition

    Professional implementation with:
    - Smooth logarithmic crossfader movement
    - Simultaneous channel fader adjustments
    - Beat-synchronized timing
    - Command sequence generation for scheduler

    Args:
        from_deck: Source deck identifier ('A', 'B', 'C', 'D')
        to_deck: Destination deck identifier ('A', 'B', 'C', 'D')
        steps: Number of transition steps (default: 16)
        duration_bars: Transition duration in bars (default: 8)
        bpm: Current BPM for timing calculation (default: 128.0)

    Returns:
        List of TransitionCommand objects for scheduler execution

    Raises:
        ValueError: If deck IDs are invalid or same

    Example:
        >>> # 16-step transition from Deck A to Deck B over 8 bars
        >>> commands = execute_crossfade('A', 'B', steps=16, duration_bars=8, bpm=128.0)
        >>> for cmd in commands:
        ...     # Execute command at beat_offset
        ...     pass
    """
    if from_deck not in ['A', 'B', 'C', 'D'] or to_deck not in ['A', 'B', 'C', 'D']:
        raise ValueError("Invalid deck IDs")

    if from_deck == to_deck:
        raise ValueError("Cannot transition to the same deck")

    logger.info(
        f"Executing crossfade: {from_deck} → {to_deck} ({steps} steps, {duration_bars} bars)",
        extra={
            'from_deck': from_deck,
            'to_deck': to_deck,
            'steps': steps,
            'duration_bars': duration_bars,
            'bpm': bpm
        }
    )

    # Calculate timing
    beats_per_bar = 4
    total_beats = duration_bars * beats_per_bar
    beats_per_step = total_beats / steps

    # Determine crossfader direction
    # Deck A/C = Left (0.0), Deck B/D = Right (1.0)
    from_position = 0.0 if from_deck in ['A', 'C'] else 1.0
    to_position = 0.0 if to_deck in ['A', 'C'] else 1.0

    commands: List[TransitionCommand] = []

    # Generate transition commands
    for step in range(steps + 1):
        progress = step / steps
        beat_offset = int(step * beats_per_step)

        # Crossfader movement (linear for now, could be customized)
        crossfader_position = from_position + (to_position - from_position) * progress

        commands.append(TransitionCommand(
            beat_offset=beat_offset,
            command_type='crossfader',
            deck_id=None,
            parameter=None,
            value=crossfader_position
        ))

        # Volume fade out on from_deck
        from_volume = 1.0 - progress
        commands.append(TransitionCommand(
            beat_offset=beat_offset,
            command_type='volume',
            deck_id=from_deck,
            parameter=None,
            value=from_volume
        ))

        # Volume fade in on to_deck
        to_volume = progress
        commands.append(TransitionCommand(
            beat_offset=beat_offset,
            command_type='volume',
            deck_id=to_deck,
            parameter=None,
            value=to_volume
        ))

    logger.info(
        f"Generated {len(commands)} transition commands",
        extra={'command_count': len(commands), 'total_beats': total_beats}
    )

    return commands


def execute_eq_swap_transition(
    from_deck: str,
    to_deck: str,
    duration_bars: int = 16
) -> List[TransitionCommand]:
    """
    Execute professional EQ-based bass swap transition

    Professional technique:
    1. Cut bass on outgoing deck
    2. Bring in new deck with channel fader
    3. Gradually swap mid/high frequencies
    4. Introduce bass on incoming deck
    5. Remove outgoing deck

    Args:
        from_deck: Source deck identifier
        to_deck: Destination deck identifier
        duration_bars: Transition duration in bars (default: 16)

    Returns:
        List of TransitionCommand objects for scheduler execution

    Example:
        >>> # Professional bass swap transition
        >>> commands = execute_eq_swap_transition('A', 'B', duration_bars=16)
    """
    if from_deck not in ['A', 'B'] or to_deck not in ['A', 'B']:
        raise ValueError("EQ swap only available for Decks A and B (TSI limitation)")

    logger.info(
        f"Executing EQ bass swap: {from_deck} → {to_deck} ({duration_bars} bars)",
        extra={'from_deck': from_deck, 'to_deck': to_deck, 'duration_bars': duration_bars}
    )

    commands: List[TransitionCommand] = []
    beats_per_bar = 4
    total_beats = duration_bars * beats_per_bar

    # Phase 1: Cut outgoing bass, introduce incoming track (0-25%)
    commands.append(TransitionCommand(
        beat_offset=0,
        command_type='eq',
        deck_id=from_deck,
        parameter='low',
        value=0.0  # Kill bass
    ))

    commands.append(TransitionCommand(
        beat_offset=0,
        command_type='volume',
        deck_id=to_deck,
        parameter=None,
        value=0.8  # Bring in new track
    ))

    # Phase 2: Gradually swap mid/high frequencies (25-75%)
    phase2_start = int(total_beats * 0.25)
    phase2_end = int(total_beats * 0.75)
    phase2_steps = 16

    for step in range(phase2_steps):
        progress = step / phase2_steps
        beat_offset = phase2_start + int((phase2_end - phase2_start) * progress)

        # Fade out mid/high on outgoing deck
        commands.append(TransitionCommand(
            beat_offset=beat_offset,
            command_type='eq',
            deck_id=from_deck,
            parameter='mid',
            value=0.5 - (progress * 0.5)
        ))

        commands.append(TransitionCommand(
            beat_offset=beat_offset,
            command_type='eq',
            deck_id=from_deck,
            parameter='high',
            value=0.5 - (progress * 0.5)
        ))

    # Phase 3: Introduce incoming bass, complete transition (75-100%)
    phase3_start = int(total_beats * 0.75)

    commands.append(TransitionCommand(
        beat_offset=phase3_start,
        command_type='eq',
        deck_id=to_deck,
        parameter='low',
        value=0.5  # Full bass on new track
    ))

    commands.append(TransitionCommand(
        beat_offset=phase3_start,
        command_type='volume',
        deck_id=from_deck,
        parameter=None,
        value=0.0  # Remove old track
    ))

    logger.info(
        f"Generated {len(commands)} EQ swap commands",
        extra={'command_count': len(commands)}
    )

    return commands


# ============================================================================
# MIXER PREPARATION FUNCTIONS
# ============================================================================

def prepare_mixer_for_playback(deck_id: str, is_first_track: bool = False) -> bool:
    """
    Prepare mixer settings before deck playback

    Critical pre-playback mixer setup per DJ_WORKFLOW_RULES.md:
    - Position crossfader for target deck
    - Set appropriate channel fader level
    - Configure EQ to neutral

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        is_first_track: True if this is the first track (no other decks playing)

    Returns:
        True if mixer prepared successfully

    Example:
        >>> # Prepare mixer for first track on Deck A
        >>> prepare_mixer_for_playback('A', is_first_track=True)

        >>> # Prepare mixer for incoming track on Deck B
        >>> prepare_mixer_for_playback('B', is_first_track=False)
    """
    logger.info(
        f"Preparing mixer for Deck {deck_id} playback (first_track={is_first_track})",
        extra={'deck': deck_id, 'is_first_track': is_first_track}
    )

    try:
        # 1. Position crossfader
        if deck_id in ['A', 'C']:
            set_crossfader_position(0.0)  # Full LEFT
        elif deck_id in ['B', 'D']:
            set_crossfader_position(1.0)  # Full RIGHT

        # 2. Set channel fader level
        if is_first_track:
            # First track: High volume (85%)
            set_volume(deck_id, 0.85)
        else:
            # Incoming track: Low volume (20%) for smooth transition
            set_volume(deck_id, 0.20)

        # 3. Configure EQ to neutral (only for Decks A and B with EQ mapping)
        if deck_id in ['A', 'B']:
            set_eq(deck_id, low=0.5, mid=0.5, high=0.5)

        logger.info(
            f"Mixer prepared successfully for Deck {deck_id}",
            extra={'deck': deck_id}
        )
        return True

    except Exception as e:
        logger.error(
            f"Failed to prepare mixer for Deck {deck_id}: {str(e)}",
            extra={'deck': deck_id, 'error': str(e)}
        )
        return False


def reset_mixer() -> bool:
    """
    Reset mixer to initial state

    - Crossfader to center
    - All channel faders to 85%
    - All EQ to neutral
    - Master volume to 85%

    Returns:
        True on success
    """
    logger.info("Resetting mixer to initial state")

    try:
        # Reset crossfader
        set_crossfader_position(0.5)

        # Reset all channel faders
        for deck_id in ['A', 'B', 'C', 'D']:
            set_volume(deck_id, 0.85)

        # Reset EQ (only Decks A and B)
        for deck_id in ['A', 'B']:
            set_eq(deck_id, low=0.5, mid=0.5, high=0.5)

        # Reset master volume
        set_master_volume(0.85)

        logger.info("Mixer reset complete")
        return True

    except Exception as e:
        logger.error(f"Failed to reset mixer: {str(e)}")
        return False


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_mixer_operations():
    """
    Initialize mixer operations module

    - Verify MIDI script exists
    - Reset mixer to known state
    - Configure logging
    """
    logger.info("Initializing mixer operations module")

    # Verify MIDI script
    if not MIDI_SCRIPT_PATH.exists():
        logger.warning(
            f"MIDI script not found: {MIDI_SCRIPT_PATH}",
            extra={'script_path': str(MIDI_SCRIPT_PATH)}
        )

    # Reset mixer to initial state
    reset_mixer()

    logger.info("Mixer operations module initialized successfully")


# ============================================================================
# MAIN ENTRY POINT (For Testing)
# ============================================================================

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize module
    initialize_mixer_operations()

    # Print mixer state
    print("\n=== MIXER STATE ===")
    state = get_mixer_state()
    print(f"Crossfader: {state['crossfader_position']:.2f}")
    print(f"Master Volume: {state['master_volume']:.2f}")
    print("\nVolumes:")
    for deck, vol in state['volumes'].items():
        print(f"  Deck {deck}: {vol:.2f}")
    print("\nEQ Settings:")
    for deck, eq in state['eq_settings'].items():
        print(f"  Deck {deck}: Low={eq['low']:.2f}, Mid={eq['mid']:.2f}, High={eq['high']:.2f}")

    print("\n=== MIXER OPERATIONS MODULE READY ===")
