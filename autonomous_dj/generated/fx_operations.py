#!/usr/bin/env python3
"""
FX Operations Module - Creative Effects Processing for Traktor Pro 3

This module provides artistic sound design and performance-oriented FX combinations
for DJ performances. Implements creative effects processing, automated build-ups,
breakdowns, and intelligent effect chains.

Author: fx-creative-agent (AI DJ System)
Date: 2025-10-09
Version: 1.0.0

Critical Dependencies:
- DEFINITIVE_CC_MAPPINGS.md: Verified FX Unit CC mappings from Traktor screenshots
- send_single_cc.py: MIDI communication via subprocess
- Creative FX Design: Build-ups, breakdowns, transitions, signature moments

FX Philosophy:
- Musical Context Awareness: Effects must enhance, not distract
- Timing & Phrase Boundaries: All effects respect musical structure
- Intensity Management: Subtle (20-40%), Moderate (50-70%), Dramatic (80-100%)
- Quality Control: Monitor for clipping, phase issues, audio degradation
"""

import subprocess
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class FXType(Enum):
    """Available effect types in Traktor Pro 3"""
    # Time-Based Effects
    DELAY = "delay"
    REVERB = "reverb"
    ECHO = "echo"

    # Modulation Effects
    FLANGER = "flanger"
    PHASER = "phaser"
    CHORUS = "chorus"
    TREMOLO = "tremolo"

    # Filter Effects
    HPF = "high_pass_filter"
    LPF = "low_pass_filter"
    PEAK_FILTER = "peak_filter"
    FORMANT = "formant_filter"

    # Distortion & Character
    OVERDRIVE = "overdrive"
    DISTORTION = "distortion"
    BIT_CRUSHER = "bit_crusher"
    TAPE_SATURATOR = "tape_saturator"

    # Creative/Special
    GATER = "gater"
    BEATMASHER = "beatmasher"
    REVERSE = "reverse"
    TURNTABLE_FX = "turntable_fx"


class FXUnit(Enum):
    """FX Unit identifiers (Traktor has 4 FX units)"""
    UNIT_1 = 1
    UNIT_2 = 2
    UNIT_3 = 3
    UNIT_4 = 4


@dataclass
class FXState:
    """
    Current state of an FX unit

    Attributes:
        unit_id: FX Unit number (1-4)
        is_active: Whether FX unit is currently ON
        dry_wet: Effect intensity (0.0-1.0)
        button_1_active: Effect slot 1 enabled
        button_2_active: Effect slot 2 enabled
        button_3_active: Effect slot 3 enabled
        knob_1_value: Parameter knob 1 (0.0-1.0)
        knob_2_value: Parameter knob 2 (0.0-1.0)
        knob_3_value: Parameter knob 3 (0.0-1.0)
        active_effects: List of currently active effect types
        assigned_deck: Which deck this FX unit is routed to (None = master)
    """
    unit_id: int
    is_active: bool = False
    dry_wet: float = 0.5
    button_1_active: bool = False
    button_2_active: bool = False
    button_3_active: bool = False
    knob_1_value: float = 0.5
    knob_2_value: float = 0.5
    knob_3_value: float = 0.5
    active_effects: List[str] = field(default_factory=list)
    assigned_deck: Optional[str] = None


@dataclass
class FXChainStep:
    """
    Single step in an automated FX sequence

    Attributes:
        fx_type: Type of effect to apply
        intensity: Effect intensity (0.0-1.0)
        duration_beats: How long this step lasts
        parameter_overrides: Custom parameter values for effect knobs
    """
    fx_type: str
    intensity: float = 0.5
    duration_beats: int = 16
    parameter_overrides: Dict[str, float] = field(default_factory=dict)


# ============================================================================
# MIDI CC MAPPING (FX Units - Verified from DEFINITIVE_CC_MAPPINGS.md)
# ============================================================================

# FX Unit 1 MIDI CC Controls
FX1_UNIT_ON = 96      # FX Unit 1 On/Off
FX1_BUTTON_1 = 93     # Effect slot 1 (Toggle mode)
FX1_BUTTON_2 = 94     # Effect slot 2 (Hold mode)
FX1_BUTTON_3 = 95     # Effect slot 3 (Hold mode)
FX1_KNOB_1 = 77       # Effect parameter 1
FX1_KNOB_2 = 78       # Effect parameter 2
FX1_KNOB_3 = 79       # Effect parameter 3
FX1_DRY_WET = 76      # Dry/Wet mix (0-127)

# FX Unit 2 MIDI CC Controls
FX2_UNIT_ON = 104
FX2_BUTTON_1 = 101
FX2_BUTTON_2 = 102
FX2_BUTTON_3 = 103
FX2_KNOB_1 = 98
FX2_KNOB_2 = 99
FX2_KNOB_3 = 100
FX2_DRY_WET = 97

# FX Unit 3 MIDI CC Controls
FX3_UNIT_ON = 112
FX3_BUTTON_1 = 109
FX3_BUTTON_2 = 110
FX3_BUTTON_3 = 111
FX3_KNOB_1 = 106
FX3_KNOB_2 = 107
FX3_KNOB_3 = 108
FX3_DRY_WET = 105

# FX Unit 4 MIDI CC Controls
FX4_UNIT_ON = 120
FX4_BUTTON_1 = 117
FX4_BUTTON_2 = 118
FX4_BUTTON_3 = 119
FX4_KNOB_1 = 114
FX4_KNOB_2 = 115
FX4_KNOB_3 = 116
FX4_DRY_WET = 113

# CC Mapping Dictionary
FX_CC_MAP = {
    1: {
        'unit_on': FX1_UNIT_ON,
        'button_1': FX1_BUTTON_1,
        'button_2': FX1_BUTTON_2,
        'button_3': FX1_BUTTON_3,
        'knob_1': FX1_KNOB_1,
        'knob_2': FX1_KNOB_2,
        'knob_3': FX1_KNOB_3,
        'dry_wet': FX1_DRY_WET,
    },
    2: {
        'unit_on': FX2_UNIT_ON,
        'button_1': FX2_BUTTON_1,
        'button_2': FX2_BUTTON_2,
        'button_3': FX2_BUTTON_3,
        'knob_1': FX2_KNOB_1,
        'knob_2': FX2_KNOB_2,
        'knob_3': FX2_KNOB_3,
        'dry_wet': FX2_DRY_WET,
    },
    3: {
        'unit_on': FX3_UNIT_ON,
        'button_1': FX3_BUTTON_1,
        'button_2': FX3_BUTTON_2,
        'button_3': FX3_BUTTON_3,
        'knob_1': FX3_KNOB_1,
        'knob_2': FX3_KNOB_2,
        'knob_3': FX3_KNOB_3,
        'dry_wet': FX3_DRY_WET,
    },
    4: {
        'unit_on': FX4_UNIT_ON,
        'button_1': FX4_BUTTON_1,
        'button_2': FX4_BUTTON_2,
        'button_3': FX4_BUTTON_3,
        'knob_1': FX4_KNOB_1,
        'knob_2': FX4_KNOB_2,
        'knob_3': FX4_KNOB_3,
        'dry_wet': FX4_DRY_WET,
    }
}


# ============================================================================
# GLOBAL STATE TRACKING
# ============================================================================

# In-memory FX states for all four units
_fx_states: Dict[int, FXState] = {
    1: FXState(unit_id=1),
    2: FXState(unit_id=2),
    3: FXState(unit_id=3),
    4: FXState(unit_id=4),
}

# Track automated effect sequences
_active_automations: Dict[int, threading.Thread] = {}

# MIDI command timeout (seconds)
MIDI_TIMEOUT_SEC = 3.0

# Path to send_single_cc.py
MIDI_SCRIPT_PATH = Path(__file__).parent.parent.parent / "tools" / "send_single_cc.py"


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
        result = subprocess.run(
            ['python3', str(MIDI_SCRIPT_PATH), str(cc_number), str(value)],
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
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode
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


def _set_fx_unit_on(unit_id: int, enable: bool) -> bool:
    """Enable/disable FX unit"""
    cc_number = FX_CC_MAP[unit_id]['unit_on']
    value = 127 if enable else 0

    success = send_midi_cc(cc_number, value)

    if success:
        _fx_states[unit_id].is_active = enable
        logger.info(
            f"FX Unit {unit_id} {'enabled' if enable else 'disabled'}",
            extra={'fx_unit': unit_id, 'active': enable}
        )

    return success


def _set_fx_dry_wet(unit_id: int, dry_wet: float) -> bool:
    """Set FX unit dry/wet mix (0.0-1.0)"""
    # Validate range
    dry_wet = max(0.0, min(1.0, dry_wet))

    # Convert to MIDI value (0-127)
    midi_value = int(dry_wet * 127)

    cc_number = FX_CC_MAP[unit_id]['dry_wet']
    success = send_midi_cc(cc_number, midi_value)

    if success:
        _fx_states[unit_id].dry_wet = dry_wet
        logger.info(
            f"FX Unit {unit_id} dry/wet set to {dry_wet:.2f}",
            extra={'fx_unit': unit_id, 'dry_wet': dry_wet, 'midi_value': midi_value}
        )

    return success


def _set_fx_button(unit_id: int, button_num: int, enable: bool) -> bool:
    """Enable/disable FX button (effect slot)"""
    cc_key = f'button_{button_num}'
    cc_number = FX_CC_MAP[unit_id][cc_key]
    value = 127 if enable else 0

    success = send_midi_cc(cc_number, value)

    if success:
        if button_num == 1:
            _fx_states[unit_id].button_1_active = enable
        elif button_num == 2:
            _fx_states[unit_id].button_2_active = enable
        elif button_num == 3:
            _fx_states[unit_id].button_3_active = enable

        logger.debug(
            f"FX Unit {unit_id} Button {button_num} {'enabled' if enable else 'disabled'}",
            extra={'fx_unit': unit_id, 'button': button_num, 'active': enable}
        )

    return success


def _set_fx_knob(unit_id: int, knob_num: int, value: float) -> bool:
    """Set FX parameter knob value (0.0-1.0)"""
    # Validate range
    value = max(0.0, min(1.0, value))

    # Convert to MIDI value (0-127)
    midi_value = int(value * 127)

    cc_key = f'knob_{knob_num}'
    cc_number = FX_CC_MAP[unit_id][cc_key]
    success = send_midi_cc(cc_number, midi_value)

    if success:
        if knob_num == 1:
            _fx_states[unit_id].knob_1_value = value
        elif knob_num == 2:
            _fx_states[unit_id].knob_2_value = value
        elif knob_num == 3:
            _fx_states[unit_id].knob_3_value = value

        logger.debug(
            f"FX Unit {unit_id} Knob {knob_num} set to {value:.2f}",
            extra={'fx_unit': unit_id, 'knob': knob_num, 'value': value}
        )

    return success


# ============================================================================
# DECK-TO-FX ROUTING HELPER
# ============================================================================

def _get_available_fx_unit() -> int:
    """
    Get first available (inactive) FX unit

    Returns:
        FX unit ID (1-4) or 1 if all busy (will override)
    """
    for unit_id in [1, 2, 3, 4]:
        if not _fx_states[unit_id].is_active:
            return unit_id

    # All units busy - use Unit 1 (common practice)
    logger.warning("All FX units busy, using Unit 1")
    return 1


def _assign_fx_unit_to_deck(unit_id: int, deck_id: str):
    """
    Mark FX unit as assigned to specific deck

    NOTE: Traktor FX routing is configured in Preferences > Effects
    This function only updates internal state for tracking purposes.
    Actual routing must be pre-configured in Traktor.

    Args:
        unit_id: FX Unit (1-4)
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
    """
    _fx_states[unit_id].assigned_deck = deck_id
    logger.debug(
        f"FX Unit {unit_id} assigned to Deck {deck_id}",
        extra={'fx_unit': unit_id, 'deck': deck_id}
    )


# ============================================================================
# CORE FX OPERATIONS
# ============================================================================

def apply_fx(deck_id: str, fx_type: str, intensity: float = 0.5, fx_unit: Optional[int] = None) -> bool:
    """
    Apply effect to deck with specified intensity

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        fx_type: Effect type (see FXType enum)
        intensity: Effect intensity (0.0-1.0)
            - 0.0-0.4: Subtle enhancement
            - 0.4-0.7: Moderate impact
            - 0.7-1.0: Dramatic moments
        fx_unit: Specific FX unit to use (1-4), None = auto-select

    Returns:
        True on success

    Raises:
        ValueError: If invalid deck_id or fx_type
        RuntimeError: If MIDI communication fails

    Example:
        >>> # Add reverb to Deck A at 60% intensity
        >>> apply_fx('A', 'reverb', intensity=0.6)

        >>> # Apply high-pass filter to Deck B (build-up effect)
        >>> apply_fx('B', 'high_pass_filter', intensity=0.8)
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}")

    # Validate intensity range
    intensity = max(0.0, min(1.0, intensity))

    # Select FX unit
    if fx_unit is None:
        fx_unit = _get_available_fx_unit()

    if fx_unit not in [1, 2, 3, 4]:
        raise ValueError(f"Invalid fx_unit: {fx_unit}. Must be 1-4")

    logger.info(
        f"Applying {fx_type} to Deck {deck_id} (Unit {fx_unit}, intensity={intensity:.2f})",
        extra={
            'deck': deck_id,
            'fx_type': fx_type,
            'intensity': intensity,
            'fx_unit': fx_unit
        }
    )

    # Assign unit to deck (internal tracking)
    _assign_fx_unit_to_deck(fx_unit, deck_id)

    # Enable FX Unit
    _set_fx_unit_on(fx_unit, True)

    # Set dry/wet to desired intensity
    _set_fx_dry_wet(fx_unit, intensity)

    # Activate Button 1 (primary effect slot)
    _set_fx_button(fx_unit, 1, True)

    # Set knob parameters based on effect type
    # NOTE: This assumes Button 1 is pre-configured with desired effect in Traktor
    if fx_type in ['reverb', 'delay', 'echo']:
        # Time-based: Higher knob 1 = more time/feedback
        _set_fx_knob(fx_unit, 1, 0.7)
    elif fx_type in ['high_pass_filter', 'low_pass_filter']:
        # Filters: Knob 1 controls cutoff frequency
        _set_fx_knob(fx_unit, 1, 0.5)
    elif fx_type in ['flanger', 'phaser']:
        # Modulation: Knob 1 controls rate
        _set_fx_knob(fx_unit, 1, 0.6)
    else:
        # Default: Set knob to neutral
        _set_fx_knob(fx_unit, 1, 0.5)

    # Update state
    _fx_states[fx_unit].active_effects = [fx_type]

    return True


def create_fx_chain(deck_id: str, fx_chain: List[Dict[str, Any]], fx_unit: Optional[int] = None) -> bool:
    """
    Apply multiple effects in sequence (FX chain)

    This uses Traktor's Group Mode where up to 3 effects can be chained.

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        fx_chain: List of effect definitions (max 3 effects)
            Each dict should have: {'type': str, 'intensity': float, 'knob_value': float}
        fx_unit: Specific FX unit to use (1-4), None = auto-select

    Returns:
        True on success

    Raises:
        ValueError: If fx_chain has >3 effects or invalid parameters

    Example:
        >>> # Build-up chain: HPF + Reverb + Delay
        >>> chain = [
        ...     {'type': 'high_pass_filter', 'intensity': 0.7, 'knob_value': 0.8},
        ...     {'type': 'reverb', 'intensity': 0.6, 'knob_value': 0.7},
        ...     {'type': 'delay', 'intensity': 0.5, 'knob_value': 0.6}
        ... ]
        >>> create_fx_chain('A', chain)
    """
    if len(fx_chain) > 3:
        raise ValueError("FX chain can have maximum 3 effects (Traktor Group Mode limit)")

    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}")

    # Select FX unit
    if fx_unit is None:
        fx_unit = _get_available_fx_unit()

    logger.info(
        f"Creating FX chain on Deck {deck_id} (Unit {fx_unit}): {len(fx_chain)} effects",
        extra={'deck': deck_id, 'fx_unit': fx_unit, 'chain_length': len(fx_chain)}
    )

    # Assign unit to deck
    _assign_fx_unit_to_deck(fx_unit, deck_id)

    # Enable FX Unit
    _set_fx_unit_on(fx_unit, True)

    # Get average intensity for dry/wet
    avg_intensity = sum(fx.get('intensity', 0.5) for fx in fx_chain) / len(fx_chain)
    _set_fx_dry_wet(fx_unit, avg_intensity)

    # Apply each effect in chain (up to 3)
    active_effects = []

    for i, fx_config in enumerate(fx_chain[:3], start=1):
        fx_type = fx_config.get('type', 'delay')
        knob_value = fx_config.get('knob_value', 0.5)

        # Enable button for this effect slot
        _set_fx_button(fx_unit, i, True)

        # Set parameter knob
        _set_fx_knob(fx_unit, i, knob_value)

        active_effects.append(fx_type)

        logger.debug(
            f"FX Chain slot {i}: {fx_type} (knob={knob_value:.2f})",
            extra={'slot': i, 'fx_type': fx_type, 'knob_value': knob_value}
        )

    # Update state
    _fx_states[fx_unit].active_effects = active_effects

    return True


def clear_fx(deck_id: str, fx_unit: Optional[int] = None) -> bool:
    """
    Remove all effects from deck (return to dry signal)

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        fx_unit: Specific FX unit to clear (1-4), None = clear all assigned to deck

    Returns:
        True on success

    Example:
        >>> # Clear all effects from Deck A
        >>> clear_fx('A')

        >>> # Clear specific FX unit
        >>> clear_fx('B', fx_unit=2)
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}")

    units_to_clear = []

    if fx_unit is not None:
        # Clear specific unit
        units_to_clear = [fx_unit]
    else:
        # Clear all units assigned to this deck
        units_to_clear = [
            uid for uid, state in _fx_states.items()
            if state.assigned_deck == deck_id and state.is_active
        ]

        if not units_to_clear:
            logger.debug(f"No active FX units for Deck {deck_id}")
            return True

    logger.info(
        f"Clearing FX from Deck {deck_id}: Units {units_to_clear}",
        extra={'deck': deck_id, 'units': units_to_clear}
    )

    success = True
    for unit_id in units_to_clear:
        try:
            # Disable all effect buttons
            _set_fx_button(unit_id, 1, False)
            _set_fx_button(unit_id, 2, False)
            _set_fx_button(unit_id, 3, False)

            # Set dry/wet to 0 (fully dry)
            _set_fx_dry_wet(unit_id, 0.0)

            # Disable FX unit
            _set_fx_unit_on(unit_id, False)

            # Reset state
            _fx_states[unit_id].active_effects = []
            _fx_states[unit_id].assigned_deck = None

        except Exception as e:
            logger.error(
                f"Failed to clear FX Unit {unit_id}: {str(e)}",
                extra={'fx_unit': unit_id, 'error': str(e)}
            )
            success = False

    return success


# ============================================================================
# AUTOMATED FX SEQUENCES (Creative Performance)
# ============================================================================

def build_up_effect(deck_id: str, duration_bars: int = 4, fx_unit: Optional[int] = None) -> bool:
    """
    Create dramatic build-up effect (automated over time)

    This applies a classic DJ build-up:
    - Phase 1-2: High-pass filter sweep + Light reverb
    - Phase 3-4: Add delay + Increase reverb

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        duration_bars: Build-up duration in bars (4/8/16 bars typical)
        fx_unit: Specific FX unit to use (1-4), None = auto-select

    Returns:
        True if build-up sequence started

    Example:
        >>> # 8-bar build-up on Deck B
        >>> build_up_effect('B', duration_bars=8)
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}")

    if fx_unit is None:
        fx_unit = _get_available_fx_unit()

    logger.info(
        f"Starting build-up effect on Deck {deck_id} ({duration_bars} bars)",
        extra={'deck': deck_id, 'duration_bars': duration_bars, 'fx_unit': fx_unit}
    )

    # Calculate timing (assuming 4 beats per bar, 120 BPM = 2 beats/sec)
    # This is approximate - ideally sync with actual BPM
    beats_per_second = 2.0  # 120 BPM
    total_duration_sec = (duration_bars * 4) / beats_per_second

    def _build_up_automation():
        """Thread function for automated build-up"""
        try:
            # Assign and enable FX unit
            _assign_fx_unit_to_deck(fx_unit, deck_id)
            _set_fx_unit_on(fx_unit, True)

            # Phase 1: HPF + Light Reverb (first half)
            phase_1_duration = total_duration_sec / 2

            # Start with low intensity
            _set_fx_dry_wet(fx_unit, 0.3)
            _set_fx_button(fx_unit, 1, True)  # HPF
            _set_fx_button(fx_unit, 2, True)  # Reverb
            _set_fx_knob(fx_unit, 1, 0.4)    # HPF cutoff low
            _set_fx_knob(fx_unit, 2, 0.4)    # Reverb size

            logger.debug(f"Build-up Phase 1: HPF + Light Reverb ({phase_1_duration:.1f}s)")

            # Gradual increase over phase 1
            steps = 10
            for step in range(steps):
                time.sleep(phase_1_duration / steps)

                # Increase intensity gradually
                intensity = 0.3 + (0.3 * (step / steps))  # 0.3 -> 0.6
                _set_fx_dry_wet(fx_unit, intensity)

                # Sweep HPF cutoff up
                cutoff = 0.4 + (0.3 * (step / steps))  # 0.4 -> 0.7
                _set_fx_knob(fx_unit, 1, cutoff)

            # Phase 2: Add Delay + Full Reverb (second half)
            phase_2_duration = total_duration_sec / 2

            _set_fx_button(fx_unit, 3, True)  # Add delay
            _set_fx_knob(fx_unit, 3, 0.6)    # Delay time

            logger.debug(f"Build-up Phase 2: HPF + Reverb + Delay ({phase_2_duration:.1f}s)")

            # Continue ramping to peak
            for step in range(steps):
                time.sleep(phase_2_duration / steps)

                # Ramp to maximum intensity
                intensity = 0.6 + (0.4 * (step / steps))  # 0.6 -> 1.0
                _set_fx_dry_wet(fx_unit, intensity)

                # Continue HPF sweep
                cutoff = 0.7 + (0.3 * (step / steps))  # 0.7 -> 1.0
                _set_fx_knob(fx_unit, 1, cutoff)

                # Increase reverb size
                reverb_size = 0.4 + (0.6 * (step / steps))  # 0.4 -> 1.0
                _set_fx_knob(fx_unit, 2, reverb_size)

            logger.info(
                f"Build-up effect completed on Deck {deck_id}",
                extra={'deck': deck_id, 'fx_unit': fx_unit}
            )

            # Keep at peak (user should manually clear or trigger drop)

        except Exception as e:
            logger.error(
                f"Build-up automation failed: {str(e)}",
                extra={'deck': deck_id, 'error': str(e)}
            )

    # Start automation in background thread
    automation_thread = threading.Thread(target=_build_up_automation, daemon=True)
    automation_thread.start()

    # Track active automation
    _active_automations[fx_unit] = automation_thread

    return True


def breakdown_effect(deck_id: str, duration_bars: int = 2, fx_unit: Optional[int] = None) -> bool:
    """
    Create breakdown effect (echo + filter, then remove)

    This applies a classic breakdown:
    - Echo with increasing feedback
    - Low-pass filter gradually closing
    - Automatic removal after duration

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        duration_bars: Breakdown duration in bars (2/4 bars typical)
        fx_unit: Specific FX unit to use (1-4), None = auto-select

    Returns:
        True if breakdown sequence started

    Example:
        >>> # 4-bar breakdown on Deck A
        >>> breakdown_effect('A', duration_bars=4)
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}")

    if fx_unit is None:
        fx_unit = _get_available_fx_unit()

    logger.info(
        f"Starting breakdown effect on Deck {deck_id} ({duration_bars} bars)",
        extra={'deck': deck_id, 'duration_bars': duration_bars, 'fx_unit': fx_unit}
    )

    # Calculate timing
    beats_per_second = 2.0  # 120 BPM
    total_duration_sec = (duration_bars * 4) / beats_per_second

    def _breakdown_automation():
        """Thread function for automated breakdown"""
        try:
            # Assign and enable FX unit
            _assign_fx_unit_to_deck(fx_unit, deck_id)
            _set_fx_unit_on(fx_unit, True)

            # Start: Echo + LPF at moderate intensity
            _set_fx_dry_wet(fx_unit, 0.7)
            _set_fx_button(fx_unit, 1, True)  # Echo
            _set_fx_button(fx_unit, 2, True)  # LPF
            _set_fx_knob(fx_unit, 1, 0.6)    # Echo feedback
            _set_fx_knob(fx_unit, 2, 0.6)    # LPF cutoff

            logger.debug(f"Breakdown: Echo + LPF ({total_duration_sec:.1f}s)")

            # Gradual filter close and echo increase
            steps = 10
            for step in range(steps):
                time.sleep(total_duration_sec / steps)

                # Increase echo feedback
                feedback = 0.6 + (0.3 * (step / steps))  # 0.6 -> 0.9
                _set_fx_knob(fx_unit, 1, feedback)

                # Close LPF (reduce cutoff)
                cutoff = 0.6 - (0.4 * (step / steps))  # 0.6 -> 0.2
                _set_fx_knob(fx_unit, 2, cutoff)

            # Breakdown complete - clear effects
            logger.info(f"Breakdown complete, clearing effects on Deck {deck_id}")

            # Gradual dry (not instant cut)
            for step in range(5):
                time.sleep(0.2)
                dry_wet = 0.7 - (0.7 * (step / 5))  # 0.7 -> 0.0
                _set_fx_dry_wet(fx_unit, dry_wet)

            # Disable all
            clear_fx(deck_id, fx_unit=fx_unit)

        except Exception as e:
            logger.error(
                f"Breakdown automation failed: {str(e)}",
                extra={'deck': deck_id, 'error': str(e)}
            )

    # Start automation in background thread
    automation_thread = threading.Thread(target=_breakdown_automation, daemon=True)
    automation_thread.start()

    # Track active automation
    _active_automations[fx_unit] = automation_thread

    return True


# ============================================================================
# STATE QUERY FUNCTIONS
# ============================================================================

def get_fx_state(deck_id: str) -> Dict[str, Any]:
    """
    Get active FX state for specified deck

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')

    Returns:
        Dictionary containing:
        {
            'active_units': [1, 2],  # FX units assigned to this deck
            'fx_chains': {
                1: ['reverb', 'delay'],
                2: ['high_pass_filter']
            },
            'intensities': {
                1: 0.7,
                2: 0.5
            }
        }

    Example:
        >>> state = get_fx_state('A')
        >>> print(f"Active FX units: {state['active_units']}")
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}")

    active_units = []
    fx_chains = {}
    intensities = {}

    for unit_id, state in _fx_states.items():
        if state.assigned_deck == deck_id and state.is_active:
            active_units.append(unit_id)
            fx_chains[unit_id] = state.active_effects
            intensities[unit_id] = state.dry_wet

    return {
        'deck_id': deck_id,
        'active_units': active_units,
        'fx_chains': fx_chains,
        'intensities': intensities,
        'has_active_fx': len(active_units) > 0
    }


def get_all_fx_states() -> Dict[int, Dict[str, Any]]:
    """
    Get states of all four FX units

    Returns:
        Dictionary mapping unit_id to state dict

    Example:
        >>> states = get_all_fx_states()
        >>> for unit_id, state in states.items():
        ...     print(f"Unit {unit_id}: {state['is_active']}")
    """
    return {
        unit_id: {
            'unit_id': state.unit_id,
            'is_active': state.is_active,
            'dry_wet': state.dry_wet,
            'active_effects': state.active_effects,
            'assigned_deck': state.assigned_deck,
            'button_states': {
                1: state.button_1_active,
                2: state.button_2_active,
                3: state.button_3_active
            },
            'knob_values': {
                1: state.knob_1_value,
                2: state.knob_2_value,
                3: state.knob_3_value
            }
        }
        for unit_id, state in _fx_states.items()
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def reset_all_fx() -> bool:
    """
    Clear all FX units and reset to initial state

    Returns:
        True on success
    """
    logger.info("Resetting all FX units to initial state")

    success = True
    for unit_id in [1, 2, 3, 4]:
        try:
            # Disable all buttons
            _set_fx_button(unit_id, 1, False)
            _set_fx_button(unit_id, 2, False)
            _set_fx_button(unit_id, 3, False)

            # Reset dry/wet
            _set_fx_dry_wet(unit_id, 0.5)

            # Disable unit
            _set_fx_unit_on(unit_id, False)

            # Reset state
            _fx_states[unit_id] = FXState(unit_id=unit_id)

        except Exception as e:
            logger.error(
                f"Failed to reset FX Unit {unit_id}: {str(e)}",
                extra={'fx_unit': unit_id, 'error': str(e)}
            )
            success = False

    # Clear automation threads
    _active_automations.clear()

    return success


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_fx_operations():
    """
    Initialize FX operations module

    - Verify MIDI script exists
    - Reset all FX units to known state
    - Configure logging
    """
    logger.info("Initializing FX operations module")

    # Verify MIDI script
    if not MIDI_SCRIPT_PATH.exists():
        logger.warning(
            f"MIDI script not found: {MIDI_SCRIPT_PATH}",
            extra={'script_path': str(MIDI_SCRIPT_PATH)}
        )

    # Reset all FX units
    reset_all_fx()

    logger.info("FX operations module initialized successfully")


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
    initialize_fx_operations()

    # Print all FX states
    print("\n=== ALL FX UNIT STATES ===")
    states = get_all_fx_states()
    for unit_id, state in states.items():
        print(f"FX Unit {unit_id}: {state}")

    print("\n=== FX OPERATIONS MODULE READY ===")
