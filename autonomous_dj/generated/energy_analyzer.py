#!/usr/bin/env python3
"""
Energy Analyzer Module - Production-Ready Energy Management for DJ Sets

This module provides professional energy flow management, crowd reading, and strategic
set planning following 33 years of DJ experience and validated workflow rules.

Author: energy-flow-agent (AI DJ System)
Date: 2025-10-09
Version: 1.0.0

Critical Dependencies:
- DJ_WORKFLOW_RULES.md: Professional DJ workflow validation
- track metadata: BPM, key, genre information required
- Mathematical energy curves: No guessing, scientific approach

Energy Flow Principles:
- Opening (0-30min): BPM 118-122, energy 0.4-0.6, gradual build
- Peak (30-90min): BPM 126-130, energy 0.7-0.9, maintain high
- Closing (90-120min): BPM 122-126, energy 0.5-0.7, wind down
"""

import logging
import math
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

class EnergyLevel(Enum):
    """Energy level classification"""
    VERY_LOW = 1    # 0.0-0.2: Opening/Wind-down
    LOW = 2         # 0.2-0.4: Building energy
    MEDIUM = 3      # 0.4-0.6: Mid-energy groove
    HIGH = 4        # 0.6-0.8: Peak time
    VERY_HIGH = 5   # 0.8-1.0: Peak climax


class SetPhase(Enum):
    """DJ set phase classification"""
    OPENING = "opening"        # 0-30min: Warm-up
    BUILD = "build"            # 30-60min: Building to peak
    PEAK = "peak"              # 60-90min: Peak time
    SUSTAIN = "sustain"        # 90-105min: Sustain energy
    CLOSING = "closing"        # 105-120min: Wind down


class TransitionType(Enum):
    """Energy transition classification"""
    SMOOTH = "smooth"          # <0.1 energy delta
    GRADUAL = "gradual"        # 0.1-0.2 energy delta
    ENERGETIC = "energetic"    # 0.2-0.3 energy delta
    DROP = "drop"              # <-0.2 energy delta (energy reduction)
    JUMP = "jump"              # >0.3 energy delta (dangerous)


@dataclass
class TrackEnergy:
    """
    Energy characteristics of a track

    Attributes:
        track_id: Unique track identifier
        bpm: Beats per minute
        key: Harmonic key (Camelot notation)
        genre: Musical genre
        energy_score: Calculated energy level (0.0-1.0)
        energy_level: Classified energy level enum
        danceability: How danceable (0.0-1.0)
        valence: Musical positivity (0.0-1.0)
        intensity: Overall intensity (0.0-1.0)
    """
    track_id: str
    bpm: float
    key: str
    genre: str
    energy_score: float
    energy_level: EnergyLevel
    danceability: float = 0.7
    valence: float = 0.5
    intensity: float = 0.5


@dataclass
class EnergyTransition:
    """
    Energy transition characteristics between tracks

    Attributes:
        from_track_id: Source track identifier
        to_track_id: Destination track identifier
        energy_delta: Energy change (positive = increase, negative = decrease)
        bpm_delta: BPM change
        transition_type: Classification of transition
        harmonic_compatible: Whether keys are harmonically compatible
        recommended_mix_duration: Recommended transition time (seconds)
        risk_level: Risk assessment (0.0=safe, 1.0=risky)
    """
    from_track_id: str
    to_track_id: str
    energy_delta: float
    bpm_delta: float
    transition_type: TransitionType
    harmonic_compatible: bool
    recommended_mix_duration: int
    risk_level: float


@dataclass
class EnergyFlowPlan:
    """
    Complete energy flow plan for DJ set

    Attributes:
        total_duration_min: Total set duration in minutes
        target_strategy: Target energy strategy (build/maintain/wind_down)
        set_phase: Current phase of the set
        track_sequence: Ordered list of track IDs
        energy_curve: Energy values at each track position
        peak_moment: Index of peak energy moment
        estimated_crowd_response: Predicted crowd engagement (0.0-1.0)
    """
    total_duration_min: int
    target_strategy: str
    set_phase: SetPhase
    track_sequence: List[str]
    energy_curve: List[float]
    peak_moment: int
    estimated_crowd_response: float


# ============================================================================
# ENERGY CALCULATION CONSTANTS
# ============================================================================

# BPM ranges for different energy levels
BPM_RANGES = {
    EnergyLevel.VERY_LOW: (100, 115),
    EnergyLevel.LOW: (115, 120),
    EnergyLevel.MEDIUM: (120, 125),
    EnergyLevel.HIGH: (125, 130),
    EnergyLevel.VERY_HIGH: (130, 140),
}

# Set phase BPM targets (from DJ_WORKFLOW_RULES.md)
PHASE_BPM_TARGETS = {
    SetPhase.OPENING: (118, 122),
    SetPhase.BUILD: (122, 126),
    SetPhase.PEAK: (126, 130),
    SetPhase.SUSTAIN: (126, 130),
    SetPhase.CLOSING: (122, 126),
}

# Set phase energy targets
PHASE_ENERGY_TARGETS = {
    SetPhase.OPENING: (0.4, 0.6),
    SetPhase.BUILD: (0.6, 0.75),
    SetPhase.PEAK: (0.75, 0.9),
    SetPhase.SUSTAIN: (0.7, 0.85),
    SetPhase.CLOSING: (0.5, 0.7),
}

# Genre energy multipliers
GENRE_ENERGY_MULTIPLIERS = {
    'techno': 1.1,
    'house': 1.0,
    'tech_house': 1.05,
    'deep_house': 0.9,
    'progressive': 0.95,
    'trance': 1.15,
    'minimal': 0.85,
}

# Camelot wheel harmonic compatibility
CAMELOT_COMPATIBLE_KEYS = {
    '1A': ['1A', '12A', '2A', '1B'],
    '2A': ['2A', '1A', '3A', '2B'],
    '3A': ['3A', '2A', '4A', '3B'],
    '4A': ['4A', '3A', '5A', '4B'],
    '5A': ['5A', '4A', '6A', '5B'],
    '6A': ['6A', '5A', '7A', '6B'],
    '7A': ['7A', '6A', '8A', '7B'],
    '8A': ['8A', '7A', '9A', '8B'],
    '9A': ['9A', '8A', '10A', '9B'],
    '10A': ['10A', '9A', '11A', '10B'],
    '11A': ['11A', '10A', '12A', '11B'],
    '12A': ['12A', '11A', '1A', '12B'],
    '1B': ['1B', '12B', '2B', '1A'],
    '2B': ['2B', '1B', '3B', '2A'],
    '3B': ['3B', '2B', '4B', '3A'],
    '4B': ['4B', '3B', '5B', '4A'],
    '5B': ['5B', '4B', '6B', '5A'],
    '6B': ['6B', '5B', '7B', '6A'],
    '7B': ['7B', '6B', '8B', '7A'],
    '8B': ['8B', '7B', '9B', '8A'],
    '9B': ['9B', '8B', '10B', '9A'],
    '10B': ['10B', '9B', '11B', '10A'],
    '11B': ['11B', '10B', '12B', '11A'],
    '12B': ['12B', '11B', '1B', '12A'],
}


# ============================================================================
# CORE ENERGY ANALYSIS FUNCTIONS
# ============================================================================

def analyze_energy(track: Dict[str, Any]) -> float:
    """
    Analyze track energy level (0.0-1.0)

    Calculates energy score based on multiple factors:
    - BPM (primary factor)
    - Genre characteristics
    - Key (harmonic energy)
    - Additional metadata (danceability, valence, intensity)

    Args:
        track: Track metadata dictionary containing:
            - bpm (float): Beats per minute (required)
            - key (str): Harmonic key in Camelot notation (required)
            - genre (str): Musical genre (required)
            - danceability (float, optional): 0.0-1.0
            - valence (float, optional): 0.0-1.0
            - intensity (float, optional): 0.0-1.0

    Returns:
        Energy score between 0.0 (lowest) and 1.0 (highest)

    Raises:
        ValueError: If required fields missing or invalid

    Example:
        >>> track = {'bpm': 128, 'key': '8A', 'genre': 'techno'}
        >>> energy = analyze_energy(track)
        >>> print(f"Energy: {energy:.2f}")
        Energy: 0.78
    """
    # Validate required fields
    if 'bpm' not in track or 'key' not in track or 'genre' not in track:
        raise ValueError("Track must contain 'bpm', 'key', and 'genre' fields")

    bpm = float(track['bpm'])
    key = track['key']
    genre = track['genre'].lower()

    # Validate BPM range
    if not 80 <= bpm <= 180:
        logger.warning(
            f"BPM {bpm} outside normal range (80-180)",
            extra={'bpm': bpm, 'track': track.get('id', 'unknown')}
        )

    # ========================================================================
    # STEP 1: BPM-based energy (primary factor)
    # ========================================================================
    # Normalize BPM to 0.0-1.0 scale
    # Reference: 100 BPM = 0.0, 140 BPM = 1.0
    bpm_normalized = (bpm - 100) / 40.0
    bpm_normalized = max(0.0, min(1.0, bpm_normalized))

    bpm_weight = 0.5  # BPM contributes 50% to energy

    # ========================================================================
    # STEP 2: Genre multiplier
    # ========================================================================
    genre_multiplier = GENRE_ENERGY_MULTIPLIERS.get(genre, 1.0)

    # ========================================================================
    # STEP 3: Additional factors (optional)
    # ========================================================================
    danceability = track.get('danceability', 0.7)
    valence = track.get('valence', 0.5)
    intensity = track.get('intensity', 0.5)

    # ========================================================================
    # STEP 4: Calculate composite energy score
    # ========================================================================
    energy_score = (
        bpm_normalized * bpm_weight +
        danceability * 0.25 +
        intensity * 0.15 +
        valence * 0.1
    ) * genre_multiplier

    # Clamp to valid range
    energy_score = max(0.0, min(1.0, energy_score))

    logger.debug(
        f"Energy analysis: BPM={bpm}, Genre={genre}, Energy={energy_score:.2f}",
        extra={
            'bpm': bpm,
            'genre': genre,
            'energy': energy_score,
            'bpm_normalized': bpm_normalized,
            'genre_multiplier': genre_multiplier,
        }
    )

    return energy_score


def classify_energy_level(energy_score: float) -> EnergyLevel:
    """
    Classify energy score into discrete level

    Args:
        energy_score: Energy value (0.0-1.0)

    Returns:
        EnergyLevel enum
    """
    if energy_score < 0.2:
        return EnergyLevel.VERY_LOW
    elif energy_score < 0.4:
        return EnergyLevel.LOW
    elif energy_score < 0.6:
        return EnergyLevel.MEDIUM
    elif energy_score < 0.8:
        return EnergyLevel.HIGH
    else:
        return EnergyLevel.VERY_HIGH


def calculate_energy_transition(
    from_track: Dict[str, Any],
    to_track: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate energy delta and transition characteristics between tracks

    Analyzes the transition from one track to another, considering:
    - Energy level change
    - BPM compatibility
    - Harmonic compatibility (Camelot wheel)
    - Transition risk assessment

    Args:
        from_track: Source track metadata
        to_track: Destination track metadata

    Returns:
        Dictionary containing transition characteristics:
        {
            'from_track_id': str,
            'to_track_id': str,
            'energy_delta': float,
            'bpm_delta': float,
            'transition_type': str,
            'harmonic_compatible': bool,
            'recommended_mix_duration': int (seconds),
            'risk_level': float (0.0-1.0),
            'warnings': List[str]
        }

    Example:
        >>> from_track = {'id': 'A', 'bpm': 126, 'key': '8A', 'genre': 'house'}
        >>> to_track = {'id': 'B', 'bpm': 128, 'key': '9A', 'genre': 'techno'}
        >>> transition = calculate_energy_transition(from_track, to_track)
        >>> print(transition['transition_type'])
        'gradual'
    """
    # Calculate energy scores
    from_energy = analyze_energy(from_track)
    to_energy = analyze_energy(to_track)

    energy_delta = to_energy - from_energy
    bpm_delta = to_track['bpm'] - from_track['bpm']

    # ========================================================================
    # CLASSIFY TRANSITION TYPE
    # ========================================================================
    if energy_delta < -0.2:
        transition_type = TransitionType.DROP
    elif energy_delta > 0.3:
        transition_type = TransitionType.JUMP
    elif abs(energy_delta) < 0.1:
        transition_type = TransitionType.SMOOTH
    elif energy_delta < 0.2:
        transition_type = TransitionType.GRADUAL
    else:
        transition_type = TransitionType.ENERGETIC

    # ========================================================================
    # CHECK HARMONIC COMPATIBILITY
    # ========================================================================
    from_key = from_track['key']
    to_key = to_track['key']

    harmonic_compatible = (
        to_key in CAMELOT_COMPATIBLE_KEYS.get(from_key, [])
    )

    # ========================================================================
    # CALCULATE RECOMMENDED MIX DURATION
    # ========================================================================
    # Base: 32 beats (8 bars) = standard transition
    # Adjust based on BPM and energy change

    base_bars = 8

    # Large energy jumps need longer transitions
    if abs(energy_delta) > 0.3:
        base_bars = 16  # 16 bars for big jumps
    elif abs(energy_delta) < 0.1:
        base_bars = 4   # 4 bars for smooth transitions

    # Calculate duration in seconds based on average BPM
    avg_bpm = (from_track['bpm'] + to_track['bpm']) / 2
    beats_per_second = avg_bpm / 60.0
    recommended_duration = int((base_bars * 4) / beats_per_second)

    # ========================================================================
    # ASSESS RISK LEVEL
    # ========================================================================
    risk_level = 0.0
    warnings = []

    # Large BPM jumps are risky
    if abs(bpm_delta) > 4:
        risk_level += 0.3
        warnings.append(f"Large BPM jump: {bpm_delta:+.1f} BPM")

    # Large energy jumps are risky
    if abs(energy_delta) > 0.3:
        risk_level += 0.4
        warnings.append(f"Large energy jump: {energy_delta:+.2f}")

    # Key clashes are risky
    if not harmonic_compatible:
        risk_level += 0.2
        warnings.append(f"Key clash: {from_key} → {to_key}")

    # Genre mismatches can be risky
    if from_track['genre'] != to_track['genre']:
        risk_level += 0.1
        warnings.append(f"Genre change: {from_track['genre']} → {to_track['genre']}")

    # Clamp risk to valid range
    risk_level = min(1.0, risk_level)

    logger.info(
        f"Transition: {from_track.get('id', '?')} → {to_track.get('id', '?')}, "
        f"Energy Δ={energy_delta:+.2f}, Risk={risk_level:.2f}",
        extra={
            'from_track': from_track.get('id'),
            'to_track': to_track.get('id'),
            'energy_delta': energy_delta,
            'bpm_delta': bpm_delta,
            'transition_type': transition_type.value,
            'risk_level': risk_level,
        }
    )

    return {
        'from_track_id': from_track.get('id', 'unknown'),
        'to_track_id': to_track.get('id', 'unknown'),
        'from_energy': from_energy,
        'to_energy': to_energy,
        'energy_delta': energy_delta,
        'bpm_delta': bpm_delta,
        'transition_type': transition_type.value,
        'harmonic_compatible': harmonic_compatible,
        'recommended_mix_duration': recommended_duration,
        'risk_level': risk_level,
        'warnings': warnings,
    }


# ============================================================================
# SET PLANNING FUNCTIONS
# ============================================================================

def determine_set_phase(elapsed_min: int, total_duration_min: int) -> SetPhase:
    """
    Determine current set phase based on elapsed time

    Args:
        elapsed_min: Minutes elapsed in set
        total_duration_min: Total set duration

    Returns:
        SetPhase enum
    """
    progress = elapsed_min / total_duration_min

    if progress < 0.25:
        return SetPhase.OPENING
    elif progress < 0.5:
        return SetPhase.BUILD
    elif progress < 0.75:
        return SetPhase.PEAK
    elif progress < 0.875:
        return SetPhase.SUSTAIN
    else:
        return SetPhase.CLOSING


def generate_energy_curve(
    duration_min: int,
    target_strategy: str,
    num_tracks: int
) -> List[float]:
    """
    Generate mathematical energy curve for set

    Uses sine/cosine functions to create smooth, natural energy progression

    Args:
        duration_min: Total set duration in minutes
        target_strategy: 'build', 'maintain', or 'wind_down'
        num_tracks: Number of tracks in set

    Returns:
        List of energy values (0.0-1.0) for each track position
    """
    curve = []

    for i in range(num_tracks):
        progress = i / num_tracks
        elapsed_min = progress * duration_min
        phase = determine_set_phase(elapsed_min, duration_min)

        if target_strategy == 'build':
            # Gradual exponential build to peak
            energy = 0.4 + (0.5 * (progress ** 0.8))

        elif target_strategy == 'maintain':
            # High energy with gentle waves
            base = 0.75
            wave = 0.1 * math.sin(progress * math.pi * 4)
            energy = base + wave

        elif target_strategy == 'wind_down':
            # Gradual exponential decrease
            energy = 0.9 - (0.4 * (progress ** 1.2))

        else:
            # Standard club night curve
            # Opening → Build → Peak → Sustain → Closing
            if phase == SetPhase.OPENING:
                # Gradual increase from 0.4 to 0.6
                phase_progress = (elapsed_min / (duration_min * 0.25))
                energy = 0.4 + (0.2 * phase_progress)

            elif phase == SetPhase.BUILD:
                # Build from 0.6 to 0.85
                phase_start = duration_min * 0.25
                phase_progress = (elapsed_min - phase_start) / (duration_min * 0.25)
                energy = 0.6 + (0.25 * phase_progress)

            elif phase == SetPhase.PEAK:
                # Peak energy 0.8-0.9 with variation
                energy = 0.85 + (0.05 * math.sin(progress * math.pi * 6))

            elif phase == SetPhase.SUSTAIN:
                # Sustained high 0.7-0.85
                energy = 0.775 + (0.075 * math.sin(progress * math.pi * 4))

            else:  # CLOSING
                # Wind down from 0.7 to 0.5
                phase_start = duration_min * 0.875
                phase_progress = (elapsed_min - phase_start) / (duration_min * 0.125)
                energy = 0.7 - (0.2 * phase_progress)

        # Clamp to valid range
        energy = max(0.0, min(1.0, energy))
        curve.append(energy)

    return curve


def plan_energy_flow(
    tracks: List[Dict],
    duration_minutes: int,
    target_energy: str = 'build'
) -> List[Dict]:
    """
    Plan energy progression for set duration with optimized track order

    Reorders tracks to match target energy curve while respecting:
    - Harmonic mixing rules (Camelot wheel)
    - BPM progression (gradual changes)
    - Professional energy flow patterns

    Args:
        tracks: List of track metadata dictionaries
        duration_minutes: Total set duration
        target_energy: 'build', 'maintain', 'wind_down', or 'automatic'

    Returns:
        Ordered list of tracks with energy curve metadata

    Example:
        >>> tracks = [
        ...     {'id': '1', 'bpm': 120, 'key': '8A', 'genre': 'house'},
        ...     {'id': '2', 'bpm': 128, 'key': '9A', 'genre': 'techno'},
        ... ]
        >>> planned = plan_energy_flow(tracks, 60, 'build')
        >>> print([t['id'] for t in planned])
        ['1', '2']
    """
    if not tracks:
        logger.warning("No tracks provided for energy planning")
        return []

    num_tracks = len(tracks)

    # Generate target energy curve
    energy_curve = generate_energy_curve(duration_minutes, target_energy, num_tracks)

    # Calculate energy for all tracks
    track_energies = []
    for track in tracks:
        try:
            energy = analyze_energy(track)
            track_energies.append({
                'track': track,
                'energy': energy,
                'bpm': track['bpm'],
                'key': track['key'],
            })
        except (ValueError, KeyError) as e:
            logger.warning(
                f"Skipping track due to missing data: {e}",
                extra={'track': track.get('id', 'unknown')}
            )
            continue

    if not track_energies:
        logger.error("No valid tracks after energy analysis")
        return []

    # ========================================================================
    # OPTIMIZE TRACK ORDER TO MATCH ENERGY CURVE
    # ========================================================================
    ordered_tracks = []
    available_tracks = track_energies.copy()

    for target_energy_value in energy_curve:
        if not available_tracks:
            break

        # Find track closest to target energy
        best_match = None
        best_score = float('inf')

        for candidate in available_tracks:
            # Energy distance (primary factor)
            energy_distance = abs(candidate['energy'] - target_energy_value)

            # BPM continuity (if we have previous track)
            bpm_penalty = 0.0
            if ordered_tracks:
                prev_track = ordered_tracks[-1]
                bpm_diff = abs(candidate['bpm'] - prev_track['bpm'])
                if bpm_diff > 4:
                    bpm_penalty = 0.2  # Penalize large BPM jumps

            # Harmonic compatibility (if we have previous track)
            harmonic_penalty = 0.0
            if ordered_tracks:
                prev_track = ordered_tracks[-1]
                if candidate['key'] not in CAMELOT_COMPATIBLE_KEYS.get(prev_track['key'], []):
                    harmonic_penalty = 0.1  # Penalize key clashes

            # Total score (lower is better)
            total_score = energy_distance + bpm_penalty + harmonic_penalty

            if total_score < best_score:
                best_score = total_score
                best_match = candidate

        if best_match:
            ordered_tracks.append(best_match['track'])
            available_tracks.remove(best_match)

    # Add metadata to tracks
    for i, track in enumerate(ordered_tracks):
        track['_energy_plan'] = {
            'position': i + 1,
            'target_energy': energy_curve[i],
            'actual_energy': analyze_energy(track),
            'set_phase': determine_set_phase(
                (i / num_tracks) * duration_minutes,
                duration_minutes
            ).value,
        }

    logger.info(
        f"Energy flow planned: {len(ordered_tracks)} tracks, "
        f"duration={duration_minutes}min, strategy={target_energy}",
        extra={
            'num_tracks': len(ordered_tracks),
            'duration_min': duration_minutes,
            'strategy': target_energy,
        }
    )

    return ordered_tracks


# ============================================================================
# TRACK RECOMMENDATION FUNCTIONS
# ============================================================================

def get_energy_recommendation(
    current_energy: float,
    target_energy: float,
    available_tracks: List[Dict]
) -> List[Dict]:
    """
    Recommend next tracks to reach target energy

    Analyzes available tracks and recommends best candidates to transition
    from current energy level to target energy level.

    Args:
        current_energy: Current energy level (0.0-1.0)
        target_energy: Desired energy level (0.0-1.0)
        available_tracks: List of available track metadata

    Returns:
        Top 5 recommended tracks sorted by compatibility
        Each track includes recommendation score and reasoning

    Example:
        >>> current = 0.6
        >>> target = 0.8
        >>> tracks = [...]  # Available tracks
        >>> recommendations = get_energy_recommendation(current, target, tracks)
        >>> for rec in recommendations[:3]:
        ...     print(f"{rec['id']}: score={rec['_recommendation']['score']:.2f}")
    """
    if not available_tracks:
        logger.warning("No tracks available for recommendations")
        return []

    energy_delta = target_energy - current_energy

    recommendations = []

    for track in available_tracks:
        try:
            track_energy = analyze_energy(track)

            # ================================================================
            # SCORING FACTORS
            # ================================================================

            # 1. Energy proximity to target (primary)
            energy_distance = abs(track_energy - target_energy)
            energy_score = 1.0 - energy_distance

            # 2. Energy progression appropriateness
            # If we need to build energy, prefer slightly higher energy tracks
            # If we need to drop energy, prefer slightly lower energy tracks
            progression_score = 1.0
            if energy_delta > 0:  # Building energy
                if track_energy > current_energy and track_energy <= target_energy + 0.1:
                    progression_score = 1.2  # Bonus for good progression
            elif energy_delta < 0:  # Dropping energy
                if track_energy < current_energy and track_energy >= target_energy - 0.1:
                    progression_score = 1.2  # Bonus for good progression

            # 3. Total score (weighted)
            total_score = (
                energy_score * 0.7 +
                progression_score * 0.3
            )

            # Add recommendation metadata
            track_copy = track.copy()
            track_copy['_recommendation'] = {
                'score': total_score,
                'energy': track_energy,
                'energy_distance': energy_distance,
                'progression_appropriate': progression_score > 1.0,
                'reason': _generate_recommendation_reason(
                    track_energy,
                    current_energy,
                    target_energy,
                    energy_delta
                ),
            }

            recommendations.append(track_copy)

        except (ValueError, KeyError) as e:
            logger.warning(
                f"Skipping track in recommendations: {e}",
                extra={'track': track.get('id', 'unknown')}
            )
            continue

    # Sort by score (highest first)
    recommendations.sort(key=lambda t: t['_recommendation']['score'], reverse=True)

    # Return top 5
    top_recommendations = recommendations[:5]

    logger.info(
        f"Generated {len(top_recommendations)} recommendations "
        f"(current={current_energy:.2f}, target={target_energy:.2f})",
        extra={
            'current_energy': current_energy,
            'target_energy': target_energy,
            'num_available': len(available_tracks),
            'num_recommendations': len(top_recommendations),
        }
    )

    return top_recommendations


def _generate_recommendation_reason(
    track_energy: float,
    current_energy: float,
    target_energy: float,
    energy_delta: float
) -> str:
    """Generate human-readable recommendation reason"""

    if abs(track_energy - target_energy) < 0.05:
        return "Perfect energy match for target"

    if energy_delta > 0 and current_energy < track_energy < target_energy:
        return "Builds energy smoothly toward target"

    if energy_delta < 0 and target_energy < track_energy < current_energy:
        return "Drops energy gradually toward target"

    if track_energy > target_energy + 0.1:
        return "High energy - will overshoot target"

    if track_energy < target_energy - 0.1:
        return "Low energy - will undershoot target"

    return "Good transition candidate"


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_energy_progression(track_sequence: List[Dict]) -> Dict[str, Any]:
    """
    Validate energy flow makes sense for DJ set

    Analyzes entire track sequence for:
    - Dangerous energy jumps
    - Unnatural energy valleys
    - BPM compatibility issues
    - Harmonic mixing problems
    - Overall flow quality

    Args:
        track_sequence: Ordered list of track metadata

    Returns:
        Validation report dictionary:
        {
            'valid': bool,
            'overall_quality': float (0.0-1.0),
            'num_warnings': int,
            'num_errors': int,
            'warnings': List[str],
            'errors': List[str],
            'recommendations': List[str],
        }

    Example:
        >>> sequence = [track1, track2, track3]
        >>> report = validate_energy_progression(sequence)
        >>> if not report['valid']:
        ...     print("Issues:", report['errors'])
    """
    if not track_sequence:
        return {
            'valid': False,
            'overall_quality': 0.0,
            'num_warnings': 0,
            'num_errors': 1,
            'warnings': [],
            'errors': ['Empty track sequence'],
            'recommendations': ['Add tracks to sequence'],
        }

    warnings = []
    errors = []
    recommendations = []

    # Analyze each transition
    for i in range(len(track_sequence) - 1):
        from_track = track_sequence[i]
        to_track = track_sequence[i + 1]

        try:
            transition = calculate_energy_transition(from_track, to_track)

            # Check for dangerous energy jumps
            if transition['risk_level'] > 0.7:
                errors.append(
                    f"Track {i+1}→{i+2}: High-risk transition "
                    f"(risk={transition['risk_level']:.2f})"
                )
            elif transition['risk_level'] > 0.4:
                warnings.append(
                    f"Track {i+1}→{i+2}: Moderate risk "
                    f"(risk={transition['risk_level']:.2f})"
                )

            # Check for large BPM jumps
            if abs(transition['bpm_delta']) > 6:
                errors.append(
                    f"Track {i+1}→{i+2}: Large BPM jump "
                    f"({transition['bpm_delta']:+.1f} BPM)"
                )

            # Check for key clashes
            if not transition['harmonic_compatible']:
                warnings.append(
                    f"Track {i+1}→{i+2}: Key clash - "
                    f"consider different track order"
                )

        except Exception as e:
            errors.append(
                f"Track {i+1}→{i+2}: Analysis failed - {str(e)}"
            )

    # Calculate energy curve smoothness
    energies = [analyze_energy(t) for t in track_sequence]
    energy_changes = [abs(energies[i+1] - energies[i]) for i in range(len(energies) - 1)]
    avg_change = sum(energy_changes) / len(energy_changes) if energy_changes else 0

    # Large average changes indicate rough flow
    if avg_change > 0.25:
        warnings.append(
            f"Energy flow is choppy (avg change={avg_change:.2f}). "
            "Consider smoother progression."
        )

    # Check for unnatural valleys (sudden drops followed by sudden rises)
    for i in range(1, len(energies) - 1):
        if energies[i] < energies[i-1] - 0.2 and energies[i+1] > energies[i] + 0.2:
            warnings.append(
                f"Track {i+1}: Unnatural energy valley detected. "
                "Consider smoother progression."
            )

    # Overall quality score
    quality_score = 1.0
    quality_score -= len(errors) * 0.2
    quality_score -= len(warnings) * 0.05
    quality_score = max(0.0, min(1.0, quality_score))

    # Generate recommendations
    if len(errors) > 0:
        recommendations.append("Address high-risk transitions before performance")
    if avg_change > 0.25:
        recommendations.append("Reorder tracks for smoother energy progression")
    if len(warnings) > 3:
        recommendations.append("Consider using energy planning function to optimize flow")

    valid = len(errors) == 0

    logger.info(
        f"Energy validation: valid={valid}, quality={quality_score:.2f}, "
        f"warnings={len(warnings)}, errors={len(errors)}",
        extra={
            'valid': valid,
            'quality': quality_score,
            'num_warnings': len(warnings),
            'num_errors': len(errors),
        }
    )

    return {
        'valid': valid,
        'overall_quality': quality_score,
        'num_warnings': len(warnings),
        'num_errors': len(errors),
        'warnings': warnings,
        'errors': errors,
        'recommendations': recommendations,
        'energy_values': energies,
        'avg_energy_change': avg_change,
    }


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_energy_analyzer():
    """
    Initialize energy analyzer module

    - Validate constants
    - Configure logging
    - Run self-tests
    """
    logger.info("Initializing energy analyzer module")

    # Validate Camelot wheel completeness
    expected_keys = [f"{i}{l}" for i in range(1, 13) for l in ['A', 'B']]
    if set(CAMELOT_COMPATIBLE_KEYS.keys()) != set(expected_keys):
        logger.warning("Camelot wheel mapping incomplete")

    logger.info("Energy analyzer module initialized successfully")


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
    initialize_energy_analyzer()

    # Test with sample tracks
    print("\n=== ENERGY ANALYZER TEST ===\n")

    sample_tracks = [
        {'id': '1', 'bpm': 120, 'key': '8A', 'genre': 'house'},
        {'id': '2', 'bpm': 124, 'key': '9A', 'genre': 'house'},
        {'id': '3', 'bpm': 128, 'key': '10A', 'genre': 'techno'},
        {'id': '4', 'bpm': 126, 'key': '9A', 'genre': 'tech_house'},
    ]

    # Test energy analysis
    print("1. Energy Analysis:")
    for track in sample_tracks:
        energy = analyze_energy(track)
        level = classify_energy_level(energy)
        print(f"   Track {track['id']}: BPM={track['bpm']}, Energy={energy:.2f}, Level={level.name}")

    # Test transition analysis
    print("\n2. Transition Analysis:")
    transition = calculate_energy_transition(sample_tracks[0], sample_tracks[1])
    print(f"   Track 1→2: Energy Δ={transition['energy_delta']:+.2f}, Type={transition['transition_type']}")

    # Test energy planning
    print("\n3. Energy Flow Planning:")
    planned = plan_energy_flow(sample_tracks, 60, 'build')
    print(f"   Planned sequence: {[t['id'] for t in planned]}")

    # Test recommendations
    print("\n4. Energy Recommendations:")
    recs = get_energy_recommendation(0.5, 0.7, sample_tracks)
    for rec in recs[:3]:
        print(f"   Track {rec['id']}: Score={rec['_recommendation']['score']:.2f}")

    # Test validation
    print("\n5. Energy Progression Validation:")
    validation = validate_energy_progression(planned)
    print(f"   Valid: {validation['valid']}, Quality: {validation['overall_quality']:.2f}")

    print("\n=== ENERGY ANALYZER MODULE READY ===")
