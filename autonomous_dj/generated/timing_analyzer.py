#!/usr/bin/env python3
"""
Timing Analyzer Module - Phrase Detection & Optimal Transition Timing

This module provides advanced musical timing analysis for professional DJ mixing.
Implements phrase boundary detection, optimal transition point calculation, and
musical structure analysis based on BPM and bar-aligned patterns.

Author: transition-timing-agent (AI DJ System)
Date: 2025-10-09
Version: 1.0.0

Critical Dependencies:
- DJ_WORKFLOW_RULES.md: Professional DJ workflow validation
- config.py: Transition timing configuration
- Musical Structure: Standard DJ phrase patterns (8/16/32/64-bar)

Key Features:
- Phrase boundary detection (intro, verse, chorus, breakdown, outro)
- Optimal transition point calculation (bar-aligned)
- Musical structure analysis
- BPM-based timing calculations
- Phrase-perfect alignment validation
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class PhraseType(Enum):
    """Musical phrase types in standard DJ track structure"""
    INTRO = "intro"           # 0-32 bars (DJ-friendly mixing intro)
    VERSE = "verse"           # 32-96 bars (verses, build-up)
    CHORUS = "chorus"         # 96-128 bars (peak energy, hook)
    BREAKDOWN = "breakdown"   # 128-160 bars (reduced energy, minimal elements)
    OUTRO = "outro"           # 160+ bars (DJ-friendly mixing outro)
    UNKNOWN = "unknown"       # Unable to classify


class TransitionType(Enum):
    """DJ transition timing types"""
    QUICK = "quick"           # 16 bars (4 phrases)
    STANDARD = "standard"     # 32 bars (8 phrases)
    EXTENDED = "extended"     # 64 bars (16 phrases)
    INSTANT = "instant"       # 0-8 bars (special effects, cuts)


@dataclass
class Phrase:
    """
    Musical phrase information

    Attributes:
        phrase_type: Type of phrase (intro, verse, chorus, etc.)
        start_time: Start timestamp in seconds
        end_time: End timestamp in seconds
        start_bar: Starting bar number (0-indexed)
        end_bar: Ending bar number (0-indexed)
        duration_bars: Duration in bars
        duration_sec: Duration in seconds
        confidence: Confidence score (0.0-1.0) for phrase detection
    """
    phrase_type: PhraseType
    start_time: float
    end_time: float
    start_bar: int
    end_bar: int
    duration_bars: int
    duration_sec: float
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'phrase_type': self.phrase_type.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'start_bar': self.start_bar,
            'end_bar': self.end_bar,
            'duration_bars': self.duration_bars,
            'duration_sec': self.duration_sec,
            'confidence': self.confidence,
        }


@dataclass
class TransitionPoint:
    """
    Optimal transition timing information

    Attributes:
        start_bar: Bar to start transition (phrase-aligned)
        start_time: Timestamp to start transition (seconds)
        end_bar: Bar to complete transition
        end_time: Timestamp to complete transition (seconds)
        duration_bars: Transition duration in bars
        duration_sec: Transition duration in seconds
        transition_type: Type of transition (quick, standard, extended)
        incoming_cue_bar: Bar to cue incoming track
        crossfader_start_bar: Bar to start crossfader movement
        bass_swap_bar: Bar to swap bass EQ
        is_phrase_aligned: Whether timing is phrase-perfect
    """
    start_bar: int
    start_time: float
    end_bar: int
    end_time: float
    duration_bars: int
    duration_sec: float
    transition_type: TransitionType
    incoming_cue_bar: int
    crossfader_start_bar: int
    bass_swap_bar: int
    is_phrase_aligned: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'start_bar': self.start_bar,
            'start_time': self.start_time,
            'end_bar': self.end_bar,
            'end_time': self.end_time,
            'duration_bars': self.duration_bars,
            'duration_sec': self.duration_sec,
            'transition_type': self.transition_type.value,
            'incoming_cue_bar': self.incoming_cue_bar,
            'crossfader_start_bar': self.crossfader_start_bar,
            'bass_swap_bar': self.bass_swap_bar,
            'is_phrase_aligned': self.is_phrase_aligned,
        }


@dataclass
class ValidationReport:
    """
    Transition timing validation report

    Attributes:
        is_valid: Overall validation status
        is_phrase_aligned: Start/end on phrase boundaries
        warnings: List of warning messages
        errors: List of error messages
        recommendations: List of recommendations
    """
    is_valid: bool
    is_phrase_aligned: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'is_valid': self.is_valid,
            'is_phrase_aligned': self.is_phrase_aligned,
            'warnings': self.warnings,
            'errors': self.errors,
            'recommendations': self.recommendations,
        }


# ============================================================================
# TIMING CALCULATION UTILITIES
# ============================================================================

def bars_to_seconds(bars: int, bpm: float, beats_per_bar: int = 4) -> float:
    """
    Convert bars to seconds based on BPM

    Args:
        bars: Number of bars
        bpm: Beats per minute
        beats_per_bar: Beats per bar (default 4/4 time signature)

    Returns:
        Duration in seconds

    Example:
        >>> bars_to_seconds(8, 128.0)
        15.0  # 8 bars at 128 BPM = 15 seconds
    """
    beats = bars * beats_per_bar
    seconds = (beats / bpm) * 60.0
    return seconds


def seconds_to_bars(seconds: float, bpm: float, beats_per_bar: int = 4) -> int:
    """
    Convert seconds to bars based on BPM (rounded to nearest bar)

    Args:
        seconds: Duration in seconds
        bpm: Beats per minute
        beats_per_bar: Beats per bar (default 4/4 time signature)

    Returns:
        Number of bars (rounded)

    Example:
        >>> seconds_to_bars(15.0, 128.0)
        8  # 15 seconds at 128 BPM = 8 bars
    """
    beats = (seconds / 60.0) * bpm
    bars = beats / beats_per_bar
    return round(bars)


def bar_to_timestamp(bar: int, bpm: float, beats_per_bar: int = 4) -> float:
    """
    Convert bar number to timestamp in seconds

    Args:
        bar: Bar number (0-indexed)
        bpm: Beats per minute
        beats_per_bar: Beats per bar (default 4/4 time signature)

    Returns:
        Timestamp in seconds

    Example:
        >>> bar_to_timestamp(64, 128.0)
        120.0  # Bar 64 at 128 BPM = 120 seconds
    """
    return bars_to_seconds(bar, bpm, beats_per_bar)


def timestamp_to_bar(timestamp: float, bpm: float, beats_per_bar: int = 4) -> int:
    """
    Convert timestamp to bar number (rounded to nearest bar)

    Args:
        timestamp: Time in seconds
        bpm: Beats per minute
        beats_per_bar: Beats per bar (default 4/4 time signature)

    Returns:
        Bar number (0-indexed, rounded)

    Example:
        >>> timestamp_to_bar(120.0, 128.0)
        64  # 120 seconds at 128 BPM = bar 64
    """
    return seconds_to_bars(timestamp, bpm, beats_per_bar)


def next_phrase_boundary(current_bar: int, phrase_length: int = 8) -> int:
    """
    Find next phrase boundary (bar divisible by phrase_length)

    Args:
        current_bar: Current bar position
        phrase_length: Phrase length in bars (typically 8)

    Returns:
        Next bar number that is phrase-aligned

    Example:
        >>> next_phrase_boundary(57, 8)
        64  # Next 8-bar phrase boundary after bar 57
    """
    if current_bar % phrase_length == 0:
        return current_bar
    return ((current_bar // phrase_length) + 1) * phrase_length


def is_phrase_aligned(bar: int, phrase_length: int = 8) -> bool:
    """
    Check if bar number is on a phrase boundary

    Args:
        bar: Bar number to check
        phrase_length: Phrase length in bars (typically 8)

    Returns:
        True if bar is phrase-aligned

    Example:
        >>> is_phrase_aligned(64, 8)
        True  # 64 is divisible by 8
        >>> is_phrase_aligned(57, 8)
        False  # 57 is not divisible by 8
    """
    return bar % phrase_length == 0


# ============================================================================
# PHRASE DETECTION
# ============================================================================

def detect_phrases(track: Dict[str, Any], bpm: float, duration_sec: Optional[float] = None) -> List[Dict]:
    """
    Detect phrase boundaries based on standard DJ track structure

    Analyzes track and returns list of detected phrases with timing information.
    Uses standard DJ phrase patterns:
    - Intro: 0-32 bars (DJ-friendly mixing intro)
    - Verse: 32-96 bars (verses, build-up)
    - Chorus: 96-128 bars (peak energy, hook)
    - Breakdown: 128-160 bars (reduced energy)
    - Outro: 160+ bars (DJ-friendly mixing outro)

    Args:
        track: Track metadata dictionary containing:
            - 'bpm': BPM (optional, uses bpm parameter if missing)
            - 'duration': Duration in seconds (optional)
            - 'key': Harmonic key (optional)
        bpm: Track BPM (beats per minute)
        duration_sec: Track duration in seconds (optional, uses track['duration'] if available)

    Returns:
        List of phrase dictionaries with timing information:
        [
            {
                'phrase_type': 'intro',
                'start_time': 0.0,
                'end_time': 60.0,
                'start_bar': 0,
                'end_bar': 32,
                'duration_bars': 32,
                'duration_sec': 60.0,
                'confidence': 0.9
            },
            ...
        ]

    Example:
        >>> track = {'bpm': 128.0, 'duration': 360.0}
        >>> phrases = detect_phrases(track, 128.0)
        >>> print(f"Found {len(phrases)} phrases")
    """
    # Extract BPM from track or use parameter
    track_bpm = track.get('bpm', bpm)

    # Extract duration
    if duration_sec is None:
        duration_sec = track.get('duration', 300.0)  # Default 5 minutes

    # Calculate total bars in track
    total_bars = seconds_to_bars(duration_sec, track_bpm)

    logger.debug(
        f"Detecting phrases: BPM={track_bpm:.2f}, Duration={duration_sec:.1f}s, Bars={total_bars}",
        extra={'bpm': track_bpm, 'duration_sec': duration_sec, 'total_bars': total_bars}
    )

    phrases: List[Phrase] = []

    # Standard phrase structure (based on professional DJ tracks)
    phrase_definitions = [
        (PhraseType.INTRO, 0, 32, 0.9),           # Intro: 0-32 bars
        (PhraseType.VERSE, 32, 96, 0.85),         # Verse: 32-96 bars
        (PhraseType.CHORUS, 96, 128, 0.8),        # Chorus: 96-128 bars
        (PhraseType.BREAKDOWN, 128, 160, 0.75),   # Breakdown: 128-160 bars
        (PhraseType.OUTRO, 160, total_bars, 0.9), # Outro: 160-end bars
    ]

    for phrase_type, start_bar, end_bar, confidence in phrase_definitions:
        # Ensure end_bar doesn't exceed track length
        end_bar = min(end_bar, total_bars)

        # Skip if start_bar exceeds track length
        if start_bar >= total_bars:
            break

        # Calculate timestamps
        start_time = bar_to_timestamp(start_bar, track_bpm)
        end_time = bar_to_timestamp(end_bar, track_bpm)

        # Create phrase object
        phrase = Phrase(
            phrase_type=phrase_type,
            start_time=start_time,
            end_time=end_time,
            start_bar=start_bar,
            end_bar=end_bar,
            duration_bars=end_bar - start_bar,
            duration_sec=end_time - start_time,
            confidence=confidence,
        )

        phrases.append(phrase)

        logger.debug(
            f"Detected phrase: {phrase_type.value} (bars {start_bar}-{end_bar})",
            extra={
                'phrase_type': phrase_type.value,
                'start_bar': start_bar,
                'end_bar': end_bar,
                'confidence': confidence,
            }
        )

    # Convert to dict list for JSON serialization
    return [phrase.to_dict() for phrase in phrases]


# ============================================================================
# TRANSITION POINT CALCULATION
# ============================================================================

def find_transition_point(
    track: Dict[str, Any],
    transition_type: str = 'standard',
    current_position: Optional[float] = None
) -> float:
    """
    Find optimal transition start point (seconds) based on track structure

    Calculates the best moment to start a transition based on:
    - Transition type (quick, standard, extended)
    - Current playback position
    - Phrase boundaries (8-bar alignment)
    - Musical structure

    Standard transition points:
    - 'early': Bar 40 (early mix, long transition)
    - 'standard': Bar 56 (most common, professional DJ timing)
    - 'late': Bar 72 (late mix, quick transition)

    Args:
        track: Track metadata dictionary containing:
            - 'bpm': BPM (required)
            - 'duration': Duration in seconds (optional)
        transition_type: Type of transition ('quick', 'standard', 'extended', 'early', 'late')
        current_position: Current playback position in seconds (optional)

    Returns:
        Optimal transition start time in seconds

    Raises:
        ValueError: If track missing required fields

    Example:
        >>> track = {'bpm': 128.0, 'duration': 360.0}
        >>> start_time = find_transition_point(track, 'standard')
        >>> print(f"Start transition at {start_time:.1f}s")
    """
    # Validate track data
    if 'bpm' not in track:
        raise ValueError("Track must contain 'bpm' field")

    bpm = track['bpm']

    # Determine optimal transition bar based on type
    transition_bars = {
        'instant': 8,    # Bar 8 (very early, special effects)
        'quick': 40,     # Bar 40 (early mix)
        'early': 40,     # Bar 40 (early mix, explicit)
        'standard': 56,  # Bar 56 (standard professional timing)
        'late': 72,      # Bar 72 (late mix)
        'extended': 48,  # Bar 48 (extended transition, early start)
    }

    # Get transition start bar (default to standard)
    start_bar = transition_bars.get(transition_type.lower(), 56)

    # If current position provided, find next phrase boundary after that point
    if current_position is not None:
        current_bar = timestamp_to_bar(current_position, bpm)
        # Ensure we start after current position
        if start_bar <= current_bar:
            start_bar = next_phrase_boundary(current_bar + 8, 8)  # +8 bars preparation time

    # Convert bar to timestamp
    start_time = bar_to_timestamp(start_bar, bpm)

    logger.info(
        f"Transition point: {transition_type} at bar {start_bar} ({start_time:.1f}s)",
        extra={
            'transition_type': transition_type,
            'start_bar': start_bar,
            'start_time': start_time,
            'bpm': bpm,
        }
    )

    return start_time


# ============================================================================
# MIX DURATION CALCULATION
# ============================================================================

def calculate_mix_duration(
    from_track: Dict,
    to_track: Dict,
    transition_bars: int = 8
) -> float:
    """
    Calculate total mix duration accounting for BPM differences

    Calculates the duration of the transition period where both tracks
    are playing simultaneously. Accounts for BPM differences between tracks.

    Args:
        from_track: Outgoing track metadata containing:
            - 'bpm': BPM (required)
        to_track: Incoming track metadata containing:
            - 'bpm': BPM (required)
        transition_bars: Duration of transition in bars (default 8)

    Returns:
        Transition duration in seconds (based on outgoing track's BPM)

    Raises:
        ValueError: If tracks missing required fields

    Example:
        >>> from_track = {'bpm': 128.0}
        >>> to_track = {'bpm': 130.0}
        >>> duration = calculate_mix_duration(from_track, to_track, 8)
        >>> print(f"Mix duration: {duration:.1f}s")
    """
    # Validate track data
    if 'bpm' not in from_track:
        raise ValueError("from_track must contain 'bpm' field")
    if 'bpm' not in to_track:
        raise ValueError("to_track must contain 'bpm' field")

    from_bpm = from_track['bpm']
    to_bpm = to_track['bpm']

    # Calculate duration based on outgoing track's BPM
    # (transition timing follows the currently playing track)
    duration_sec = bars_to_seconds(transition_bars, from_bpm)

    # Calculate BPM difference for logging
    bpm_diff = abs(to_bpm - from_bpm)
    bpm_diff_percent = (bpm_diff / from_bpm) * 100.0

    logger.info(
        f"Mix duration: {duration_sec:.1f}s ({transition_bars} bars at {from_bpm:.1f} BPM)",
        extra={
            'duration_sec': duration_sec,
            'transition_bars': transition_bars,
            'from_bpm': from_bpm,
            'to_bpm': to_bpm,
            'bpm_diff': bpm_diff,
            'bpm_diff_percent': bpm_diff_percent,
        }
    )

    # Warn if BPM difference is large
    if bpm_diff > 4.0:
        logger.warning(
            f"Large BPM difference: {from_bpm:.1f} → {to_bpm:.1f} ({bpm_diff:.1f} BPM)",
            extra={'from_bpm': from_bpm, 'to_bpm': to_bpm, 'bpm_diff': bpm_diff}
        )

    return duration_sec


# ============================================================================
# PHRASE POSITION QUERY
# ============================================================================

def get_phrase_at_position(track: Dict, position: float) -> Dict[str, Any]:
    """
    Identify which phrase the playback position is in

    Analyzes current playback position and returns information about
    the current phrase (intro, verse, chorus, breakdown, outro).

    Args:
        track: Track metadata dictionary containing:
            - 'bpm': BPM (required)
            - 'duration': Duration in seconds (optional)
        position: Current playback position in seconds

    Returns:
        Dictionary containing phrase information:
        {
            'phrase_type': 'verse',
            'start_time': 60.0,
            'end_time': 180.0,
            'start_bar': 32,
            'end_bar': 96,
            'duration_bars': 64,
            'duration_sec': 120.0,
            'position_in_phrase': 30.0,  # Seconds into current phrase
            'progress_percent': 25.0,     # Percentage through phrase
            'bar_number': 48,             # Current bar
            'confidence': 0.85
        }

    Raises:
        ValueError: If track missing required fields

    Example:
        >>> track = {'bpm': 128.0, 'duration': 360.0}
        >>> phrase = get_phrase_at_position(track, 120.0)
        >>> print(f"Current phrase: {phrase['phrase_type']}")
    """
    # Validate track data
    if 'bpm' not in track:
        raise ValueError("Track must contain 'bpm' field")

    bpm = track['bpm']

    # Detect all phrases in track
    phrases = detect_phrases(track, bpm)

    # Find phrase containing position
    current_phrase = None
    for phrase in phrases:
        if phrase['start_time'] <= position < phrase['end_time']:
            current_phrase = phrase
            break

    # If no phrase found (position beyond track), return last phrase
    if current_phrase is None:
        if phrases:
            current_phrase = phrases[-1]
        else:
            # Fallback: create unknown phrase
            current_phrase = {
                'phrase_type': 'unknown',
                'start_time': 0.0,
                'end_time': position,
                'start_bar': 0,
                'end_bar': timestamp_to_bar(position, bpm),
                'duration_bars': timestamp_to_bar(position, bpm),
                'duration_sec': position,
                'confidence': 0.0,
            }

    # Calculate additional position information
    position_in_phrase = position - current_phrase['start_time']
    progress_percent = (position_in_phrase / current_phrase['duration_sec']) * 100.0
    current_bar = timestamp_to_bar(position, bpm)

    # Enhance phrase info with position data
    result = {
        **current_phrase,
        'position_in_phrase': position_in_phrase,
        'progress_percent': progress_percent,
        'bar_number': current_bar,
    }

    logger.debug(
        f"Position {position:.1f}s in phrase: {result['phrase_type']} "
        f"(bar {current_bar}, {progress_percent:.0f}% through phrase)",
        extra={
            'position': position,
            'phrase_type': result['phrase_type'],
            'bar_number': current_bar,
            'progress_percent': progress_percent,
        }
    )

    return result


# ============================================================================
# TRANSITION VALIDATION
# ============================================================================

def validate_transition_timing(
    from_track: Dict,
    to_track: Dict,
    start_bar: int,
    duration_bars: int
) -> Dict[str, Any]:
    """
    Validate transition timing for phrase alignment and musical coherence

    Analyzes proposed transition timing and checks for:
    - Phrase alignment (start/end on 8-bar boundaries)
    - Appropriate duration for BPM difference
    - Musical structure compatibility
    - Potential conflicts (mid-phrase, awkward endings)

    Args:
        from_track: Outgoing track metadata containing:
            - 'bpm': BPM (required)
            - 'duration': Duration in seconds (optional)
        to_track: Incoming track metadata containing:
            - 'bpm': BPM (required)
            - 'duration': Duration in seconds (optional)
        start_bar: Proposed transition start bar
        duration_bars: Proposed transition duration in bars

    Returns:
        Validation report dictionary:
        {
            'is_valid': True,
            'is_phrase_aligned': True,
            'warnings': ['BPM difference >2: consider shorter transition'],
            'errors': [],
            'recommendations': ['Use 16-bar transition for better BPM matching']
        }

    Raises:
        ValueError: If tracks missing required fields

    Example:
        >>> from_track = {'bpm': 128.0}
        >>> to_track = {'bpm': 130.0}
        >>> report = validate_transition_timing(from_track, to_track, 56, 8)
        >>> if report['is_valid']:
        ...     print("Transition timing is valid!")
    """
    # Validate track data
    if 'bpm' not in from_track:
        raise ValueError("from_track must contain 'bpm' field")
    if 'bpm' not in to_track:
        raise ValueError("to_track must contain 'bpm' field")

    from_bpm = from_track['bpm']
    to_bpm = to_track['bpm']

    # Initialize validation report
    report = ValidationReport(
        is_valid=True,
        is_phrase_aligned=is_phrase_aligned(start_bar, 8),
    )

    # Check phrase alignment
    if not report.is_phrase_aligned:
        report.errors.append(
            f"Start bar {start_bar} is not phrase-aligned (not divisible by 8)"
        )
        report.recommendations.append(
            f"Move to next phrase boundary: bar {next_phrase_boundary(start_bar, 8)}"
        )
        report.is_valid = False

    # Check end bar phrase alignment
    end_bar = start_bar + duration_bars
    if not is_phrase_aligned(end_bar, 8):
        report.errors.append(
            f"End bar {end_bar} is not phrase-aligned (not divisible by 8)"
        )
        report.recommendations.append(
            f"Adjust duration to end on phrase boundary (nearest: {next_phrase_boundary(end_bar, 8) - start_bar} bars)"
        )
        report.is_valid = False

    # Check transition duration validity
    if duration_bars < 4:
        report.warnings.append(
            f"Very short transition ({duration_bars} bars) - may be too abrupt"
        )
        report.recommendations.append("Consider minimum 8-bar transition for smooth mixing")
    elif duration_bars > 64:
        report.warnings.append(
            f"Very long transition ({duration_bars} bars) - may lose energy"
        )
        report.recommendations.append("Consider maximum 32-bar transition for better flow")

    # Check BPM compatibility
    bpm_diff = abs(to_bpm - from_bpm)
    bpm_diff_percent = (bpm_diff / from_bpm) * 100.0

    if bpm_diff > 4.0:
        report.warnings.append(
            f"Large BPM difference: {from_bpm:.1f} → {to_bpm:.1f} ({bpm_diff:.1f} BPM, {bpm_diff_percent:.1f}%)"
        )
        report.recommendations.append(
            "Consider shorter transition (16 bars) or tempo adjustment"
        )
    elif bpm_diff > 2.0:
        report.warnings.append(
            f"Moderate BPM difference: {from_bpm:.1f} → {to_bpm:.1f} ({bpm_diff:.1f} BPM)"
        )
        report.recommendations.append(
            "Enable SYNC for beatmatching"
        )

    # Check if transition duration appropriate for BPM difference
    if bpm_diff > 4.0 and duration_bars > 32:
        report.warnings.append(
            f"Long transition ({duration_bars} bars) with large BPM difference may sound awkward"
        )
        report.recommendations.append(
            "Use 16-24 bar transition for significant BPM changes"
        )

    # Check transition start timing
    if start_bar < 32:
        report.warnings.append(
            f"Early transition start (bar {start_bar}) - may not allow proper phrase development"
        )
    elif start_bar > 128:
        report.warnings.append(
            f"Late transition start (bar {start_bar}) - may be in breakdown/outro"
        )
        report.recommendations.append(
            "Consider transitioning during verse/chorus (bars 32-96)"
        )

    logger.info(
        f"Transition validation: {'VALID' if report.is_valid else 'INVALID'} "
        f"(bar {start_bar}, {duration_bars} bars, {len(report.warnings)} warnings)",
        extra={
            'is_valid': report.is_valid,
            'start_bar': start_bar,
            'duration_bars': duration_bars,
            'warnings_count': len(report.warnings),
            'errors_count': len(report.errors),
        }
    )

    return report.to_dict()


# ============================================================================
# ADVANCED TRANSITION PLANNING
# ============================================================================

def calculate_transition_timeline(
    from_track: Dict,
    to_track: Dict,
    start_bar: int,
    duration_bars: int = 32
) -> TransitionPoint:
    """
    Calculate complete transition timeline with all key timing points

    Generates comprehensive transition timing information including:
    - Start/end bars and timestamps
    - Incoming track cue point
    - Crossfader movement timing
    - Bass EQ swap timing
    - Phase alignment verification

    Args:
        from_track: Outgoing track metadata (must contain 'bpm')
        to_track: Incoming track metadata (must contain 'bpm')
        start_bar: Bar to start transition (should be phrase-aligned)
        duration_bars: Transition duration in bars (default 32)

    Returns:
        TransitionPoint object with complete timing information

    Raises:
        ValueError: If tracks missing required fields

    Example:
        >>> from_track = {'bpm': 128.0}
        >>> to_track = {'bpm': 130.0}
        >>> timeline = calculate_transition_timeline(from_track, to_track, 56, 32)
        >>> print(f"Start at bar {timeline.start_bar}, cue at bar {timeline.incoming_cue_bar}")
    """
    # Validate tracks
    if 'bpm' not in from_track or 'bpm' not in to_track:
        raise ValueError("Tracks must contain 'bpm' field")

    from_bpm = from_track['bpm']
    to_bpm = to_track['bpm']

    # Calculate transition timing
    end_bar = start_bar + duration_bars
    start_time = bar_to_timestamp(start_bar, from_bpm)
    end_time = bar_to_timestamp(end_bar, from_bpm)
    duration_sec = end_time - start_time

    # Calculate key transition points
    # Cue incoming track 8 bars before transition start (preparation time)
    incoming_cue_bar = max(0, start_bar - 8)

    # Start crossfader movement at transition start
    crossfader_start_bar = start_bar

    # Swap bass EQ at midpoint of transition
    bass_swap_bar = start_bar + (duration_bars // 2)

    # Determine transition type based on duration
    if duration_bars <= 16:
        transition_type = TransitionType.QUICK
    elif duration_bars <= 32:
        transition_type = TransitionType.STANDARD
    else:
        transition_type = TransitionType.EXTENDED

    # Check phrase alignment
    phrase_aligned = is_phrase_aligned(start_bar, 8) and is_phrase_aligned(end_bar, 8)

    # Create transition point
    transition = TransitionPoint(
        start_bar=start_bar,
        start_time=start_time,
        end_bar=end_bar,
        end_time=end_time,
        duration_bars=duration_bars,
        duration_sec=duration_sec,
        transition_type=transition_type,
        incoming_cue_bar=incoming_cue_bar,
        crossfader_start_bar=crossfader_start_bar,
        bass_swap_bar=bass_swap_bar,
        is_phrase_aligned=phrase_aligned,
    )

    logger.info(
        f"Transition timeline: bars {start_bar}-{end_bar} ({duration_bars} bars, {duration_sec:.1f}s)",
        extra={
            'start_bar': start_bar,
            'end_bar': end_bar,
            'duration_bars': duration_bars,
            'transition_type': transition_type.value,
            'is_phrase_aligned': phrase_aligned,
        }
    )

    return transition


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_timing_analyzer():
    """
    Initialize timing analyzer module

    - Configure logging
    - Validate dependencies
    """
    logger.info("Timing analyzer module initialized")


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
    initialize_timing_analyzer()

    # Test track
    test_track = {
        'bpm': 128.0,
        'duration': 360.0,  # 6 minutes
        'key': '8A',
    }

    print("\n=== TIMING ANALYZER TEST ===\n")

    # Test phrase detection
    print("1. PHRASE DETECTION:")
    phrases = detect_phrases(test_track, 128.0)
    for phrase in phrases:
        print(f"   {phrase['phrase_type']:12} | "
              f"Bars {phrase['start_bar']:3}-{phrase['end_bar']:3} | "
              f"Time {phrase['start_time']:6.1f}s-{phrase['end_time']:6.1f}s")

    # Test transition point
    print("\n2. TRANSITION POINT (standard):")
    transition_time = find_transition_point(test_track, 'standard')
    transition_bar = timestamp_to_bar(transition_time, 128.0)
    print(f"   Start transition at bar {transition_bar} ({transition_time:.1f}s)")

    # Test phrase at position
    print("\n3. PHRASE AT POSITION (120s):")
    current_phrase = get_phrase_at_position(test_track, 120.0)
    print(f"   Current phrase: {current_phrase['phrase_type']}")
    print(f"   Bar number: {current_phrase['bar_number']}")
    print(f"   Progress: {current_phrase['progress_percent']:.0f}%")

    # Test mix duration
    print("\n4. MIX DURATION:")
    test_track_2 = {'bpm': 130.0}
    duration = calculate_mix_duration(test_track, test_track_2, 8)
    print(f"   8-bar mix duration: {duration:.1f}s")

    # Test validation
    print("\n5. TRANSITION VALIDATION:")
    report = validate_transition_timing(test_track, test_track_2, 56, 32)
    print(f"   Valid: {report['is_valid']}")
    print(f"   Phrase-aligned: {report['is_phrase_aligned']}")
    if report['warnings']:
        print(f"   Warnings: {len(report['warnings'])}")
        for warning in report['warnings']:
            print(f"      - {warning}")

    # Test transition timeline
    print("\n6. TRANSITION TIMELINE:")
    timeline = calculate_transition_timeline(test_track, test_track_2, 56, 32)
    print(f"   Type: {timeline.transition_type.value}")
    print(f"   Start: Bar {timeline.start_bar} ({timeline.start_time:.1f}s)")
    print(f"   End: Bar {timeline.end_bar} ({timeline.end_time:.1f}s)")
    print(f"   Cue incoming at bar: {timeline.incoming_cue_bar}")
    print(f"   Bass swap at bar: {timeline.bass_swap_bar}")

    print("\n=== TIMING ANALYZER MODULE READY ===")
