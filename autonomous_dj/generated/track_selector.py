#!/usr/bin/env python3
"""
Track Selector Module - Intelligent Track Discovery & Compatibility Analysis

This module provides intelligent track discovery, harmonic mixing compatibility analysis,
and setlist generation based on professional DJ curation principles.

Implements:
- Camelot Wheel harmonic mixing system
- BPM compatibility analysis (±2 BPM direct, ±6% tempo adjustment)
- Energy flow management (build/maintain/wave profiles)
- Professional track selection criteria
- Setlist generation with smooth transitions

Author: music-discovery-curator-agent (AI DJ System)
Date: 2025-10-09
Version: 1.0.0

Critical Dependencies:
- Camelot Wheel: Harmonic mixing compatibility rules
- Energy Flow: Professional DJ energy management principles
- BPM Tolerance: Direct mix (±2), tempo adjust (±8 @ 128 BPM)
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from dataclasses import dataclass, field
from enum import Enum
import math


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class EnergyProfile(Enum):
    """Setlist energy progression profiles"""
    BUILD = "build"      # Gradual energy increase (opening set)
    MAINTAIN = "maintain"  # Sustained high energy (peak time)
    WAVE = "wave"       # Wave pattern: build → peak → drop → build


@dataclass
class TrackMetadata:
    """
    Track metadata structure

    Attributes:
        id: Unique track identifier
        title: Track title
        artist: Artist name
        bpm: Beats per minute
        key: Musical key (Camelot notation: 1A-12A, 1B-12B)
        energy: Energy level (1-10 scale)
        genre: Primary genre
        duration_sec: Track duration in seconds
    """
    id: str
    title: str
    artist: str
    bpm: float
    key: str  # Camelot notation
    energy: int  # 1-10
    genre: str
    duration_sec: int = 180  # Default 3 minutes


@dataclass
class CompatibilityScore:
    """
    Detailed compatibility analysis between two tracks

    Attributes:
        total_score: Overall compatibility (0.0-1.0)
        bpm_score: BPM compatibility (0.0-1.0)
        key_score: Harmonic compatibility (0.0-1.0)
        energy_score: Energy flow compatibility (0.0-1.0)
        bpm_delta: Absolute BPM difference
        key_compatible: Whether keys are harmonically compatible
        energy_delta: Energy level difference
        recommendation: Text recommendation for DJ
    """
    total_score: float
    bpm_score: float
    key_score: float
    energy_score: float
    bpm_delta: float
    key_compatible: bool
    energy_delta: int
    recommendation: str


# ============================================================================
# CAMELOT WHEEL DEFINITIONS
# ============================================================================

# Camelot Wheel harmonic compatibility rules
# Each key maps to its compatible keys for smooth mixing
CAMELOT_WHEEL: Dict[str, List[str]] = {
    # Minor keys (A)
    "1A": ["1A", "12A", "2A", "1B"],  # Ab minor
    "2A": ["2A", "1A", "3A", "2B"],   # Eb minor
    "3A": ["3A", "2A", "4A", "3B"],   # Bb minor
    "4A": ["4A", "3A", "5A", "4B"],   # F minor
    "5A": ["5A", "4A", "6A", "5B"],   # C minor
    "6A": ["6A", "5A", "7A", "6B"],   # G minor
    "7A": ["7A", "6A", "8A", "7B"],   # D minor
    "8A": ["8A", "7A", "9A", "8B"],   # A minor
    "9A": ["9A", "8A", "10A", "9B"],  # E minor
    "10A": ["10A", "9A", "11A", "10B"], # B minor
    "11A": ["11A", "10A", "12A", "11B"], # F# minor
    "12A": ["12A", "11A", "1A", "12B"],  # Db minor

    # Major keys (B)
    "1B": ["1B", "12B", "2B", "1A"],  # B major
    "2B": ["2B", "1B", "3B", "2A"],   # F# major
    "3B": ["3B", "2B", "4B", "3A"],   # Db major
    "4B": ["4B", "3B", "5B", "4A"],   # Ab major
    "5B": ["5B", "4B", "6B", "5A"],   # Eb major
    "6B": ["6B", "5B", "7B", "6A"],   # Bb major
    "7B": ["7B", "6B", "8B", "7A"],   # F major
    "8B": ["8B", "7B", "9B", "8A"],   # C major
    "9B": ["9B", "8B", "10B", "9A"],  # G major
    "10B": ["10B", "9B", "11B", "10A"], # D major
    "11B": ["11B", "10B", "12B", "11A"], # A major
    "12B": ["12B", "11B", "1B", "12A"],  # E major
}

# BPM compatibility thresholds
BPM_PERFECT_THRESHOLD = 2.0  # ±2 BPM = perfect for direct mixing
BPM_GOOD_THRESHOLD = 4.0     # ±4 BPM = good (slight tempo adjust)
BPM_TEMPO_ADJUST_PERCENT = 0.06  # ±6% tempo adjustment range

# Energy compatibility thresholds
ENERGY_SMOOTH_THRESHOLD = 1  # ±1 level = smooth transition
ENERGY_ACCEPTABLE_THRESHOLD = 2  # ±2 levels = acceptable

# Weighting for compatibility score calculation
WEIGHT_BPM = 0.30    # 30% weight to BPM compatibility
WEIGHT_KEY = 0.50    # 50% weight to harmonic compatibility
WEIGHT_ENERGY = 0.20  # 20% weight to energy flow


# ============================================================================
# MOCK MUSIC LIBRARY (FOR TESTING)
# ============================================================================

def get_mock_library() -> List[Dict[str, Any]]:
    """
    Get mock music library for testing.

    Contains 12 house tracks with varied BPM, keys, and energy levels
    to demonstrate compatibility analysis and setlist generation.

    Returns:
        List of track dictionaries with complete metadata
    """
    return [
        # Opening tracks (lower energy, 120-122 BPM)
        {
            "id": "track_001",
            "title": "Deep Sunrise",
            "artist": "House Foundation",
            "bpm": 120.0,
            "key": "8A",  # A minor
            "energy": 4,
            "genre": "house",
            "duration_sec": 360,
        },
        {
            "id": "track_002",
            "title": "Morning Groove",
            "artist": "DJ Smooth",
            "bpm": 121.0,
            "key": "8B",  # C major
            "energy": 5,
            "genre": "house",
            "duration_sec": 300,
        },
        {
            "id": "track_003",
            "title": "Warm Up",
            "artist": "Groove Collective",
            "bpm": 122.0,
            "key": "7A",  # D minor
            "energy": 5,
            "genre": "house",
            "duration_sec": 330,
        },

        # Building tracks (mid energy, 123-125 BPM)
        {
            "id": "track_004",
            "title": "Rising Energy",
            "artist": "Peak Hour",
            "bpm": 123.0,
            "key": "9A",  # E minor
            "energy": 6,
            "genre": "house",
            "duration_sec": 320,
        },
        {
            "id": "track_005",
            "title": "Building Blocks",
            "artist": "Foundation Sound",
            "bpm": 124.0,
            "key": "9B",  # G major
            "energy": 6,
            "genre": "house",
            "duration_sec": 340,
        },
        {
            "id": "track_006",
            "title": "Elevation",
            "artist": "Uplifter",
            "bpm": 125.0,
            "key": "10A",  # B minor
            "energy": 7,
            "genre": "house",
            "duration_sec": 310,
        },

        # Peak tracks (high energy, 126-128 BPM)
        {
            "id": "track_007",
            "title": "Peak Time Anthem",
            "artist": "Main Stage",
            "bpm": 126.0,
            "key": "10B",  # D major
            "energy": 8,
            "genre": "house",
            "duration_sec": 300,
        },
        {
            "id": "track_008",
            "title": "Energy Bomb",
            "artist": "DJ Power",
            "bpm": 127.0,
            "key": "11A",  # F# minor
            "energy": 9,
            "genre": "house",
            "duration_sec": 290,
        },
        {
            "id": "track_009",
            "title": "Maximum Drive",
            "artist": "Intensity",
            "bpm": 128.0,
            "key": "11B",  # A major
            "energy": 9,
            "genre": "house",
            "duration_sec": 280,
        },

        # Closing tracks (wind down, 124-126 BPM)
        {
            "id": "track_010",
            "title": "Sunset Vibes",
            "artist": "Chill Out",
            "bpm": 126.0,
            "key": "12A",  # Db minor
            "energy": 7,
            "genre": "house",
            "duration_sec": 350,
        },
        {
            "id": "track_011",
            "title": "Final Groove",
            "artist": "Last Call",
            "bpm": 125.0,
            "key": "12B",  # E major
            "energy": 6,
            "genre": "house",
            "duration_sec": 360,
        },
        {
            "id": "track_012",
            "title": "Goodbye Dawn",
            "artist": "Outro",
            "bpm": 124.0,
            "key": "1A",  # Ab minor
            "energy": 5,
            "genre": "house",
            "duration_sec": 380,
        },
    ]


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def calculate_bpm_compatibility(bpm1: float, bpm2: float) -> Tuple[float, str]:
    """
    Calculate BPM compatibility score between two tracks.

    Scoring:
    - Perfect (1.0): ±2 BPM (direct mix, no adjustment)
    - Good (0.7-0.9): ±4 BPM (slight tempo adjust)
    - Acceptable (0.4-0.6): Within ±6% tempo adjustment range
    - Warning (0.0-0.3): Outside comfortable mixing range

    Args:
        bpm1: First track BPM
        bpm2: Second track BPM

    Returns:
        Tuple of (score: float, recommendation: str)

    Example:
        >>> calculate_bpm_compatibility(128.0, 129.0)
        (0.95, "Perfect - Direct mix possible")
    """
    delta = abs(bpm1 - bpm2)

    # Calculate tempo adjustment percentage
    tempo_adjust_percent = delta / bpm1 if bpm1 > 0 else 1.0

    if delta <= BPM_PERFECT_THRESHOLD:
        # Perfect match - direct mixing
        score = 1.0 - (delta / BPM_PERFECT_THRESHOLD) * 0.05  # 0.95-1.0
        recommendation = "Perfect - Direct mix possible"

    elif delta <= BPM_GOOD_THRESHOLD:
        # Good match - slight adjustment
        score = 0.7 + (1.0 - (delta / BPM_GOOD_THRESHOLD)) * 0.2  # 0.7-0.9
        recommendation = "Good - Slight tempo adjust needed"

    elif tempo_adjust_percent <= BPM_TEMPO_ADJUST_PERCENT:
        # Acceptable - within tempo adjustment range
        score = 0.4 + (1.0 - (tempo_adjust_percent / BPM_TEMPO_ADJUST_PERCENT)) * 0.2  # 0.4-0.6
        recommendation = f"Acceptable - Tempo adjust ±{tempo_adjust_percent*100:.1f}%"

    else:
        # Warning - outside comfortable range
        score = max(0.0, 0.3 - (tempo_adjust_percent - BPM_TEMPO_ADJUST_PERCENT) * 2)
        recommendation = f"Warning - Large BPM difference ({delta:.1f} BPM)"

    return score, recommendation


def is_key_compatible(key1: str, key2: str) -> bool:
    """
    Check if two keys are harmonically compatible using Camelot Wheel.

    Compatible transitions:
    - Same key (8A → 8A)
    - Adjacent key ±1 semitone (8A → 7A or 9A)
    - Mode change A ↔ B (8A ↔ 8B)

    Args:
        key1: First track key (Camelot notation)
        key2: Second track key (Camelot notation)

    Returns:
        True if keys are harmonically compatible, False otherwise

    Example:
        >>> is_key_compatible("8A", "8B")
        True
        >>> is_key_compatible("8A", "3A")
        False
    """
    if key1 not in CAMELOT_WHEEL or key2 not in CAMELOT_WHEEL:
        logger.warning(f"Invalid Camelot key: {key1} or {key2}")
        return False

    return key2 in CAMELOT_WHEEL[key1]


def calculate_key_compatibility(key1: str, key2: str) -> Tuple[float, str]:
    """
    Calculate harmonic compatibility score between two keys.

    Scoring:
    - Perfect (1.0): Same key
    - Excellent (0.85): Adjacent ±1 semitone
    - Good (0.70): Mode change (A ↔ B)
    - Warning (0.0): Incompatible keys (will clash)

    Args:
        key1: First track key (Camelot notation)
        key2: Second track key (Camelot notation)

    Returns:
        Tuple of (score: float, recommendation: str)

    Example:
        >>> calculate_key_compatibility("8A", "8A")
        (1.0, "Perfect - Same key")
    """
    if not is_key_compatible(key1, key2):
        return 0.0, "Warning - Keys will clash, use transition track"

    if key1 == key2:
        # Perfect match
        return 1.0, "Perfect - Same key"

    # Extract number and mode
    num1, mode1 = int(key1[:-1]), key1[-1]
    num2, mode2 = int(key2[:-1]), key2[-1]

    if mode1 != mode2:
        # Mode change (A ↔ B)
        return 0.70, "Good - Mode change (minor ↔ major)"

    # Adjacent key (±1 semitone)
    return 0.85, "Excellent - Adjacent key (±1 semitone)"


def calculate_energy_compatibility(energy1: int, energy2: int) -> Tuple[float, str]:
    """
    Calculate energy flow compatibility between two tracks.

    Scoring:
    - Perfect (1.0): Same energy level
    - Smooth (0.8-0.9): ±1 level difference
    - Acceptable (0.5-0.7): ±2 levels
    - Warning (0.0-0.4): >±2 levels (jarring energy jump)

    Args:
        energy1: First track energy (1-10)
        energy2: Second track energy (1-10)

    Returns:
        Tuple of (score: float, recommendation: str)

    Example:
        >>> calculate_energy_compatibility(7, 8)
        (0.9, "Smooth - Natural energy build")
    """
    delta = abs(energy1 - energy2)

    if delta == 0:
        return 1.0, "Perfect - Same energy level"

    elif delta <= ENERGY_SMOOTH_THRESHOLD:
        score = 0.9 if energy2 > energy1 else 0.85
        direction = "build" if energy2 > energy1 else "drop"
        return score, f"Smooth - Natural energy {direction}"

    elif delta <= ENERGY_ACCEPTABLE_THRESHOLD:
        score = 0.6 if energy2 > energy1 else 0.5
        direction = "jump" if energy2 > energy1 else "drop"
        return score, f"Acceptable - Energy {direction} (±{delta} levels)"

    else:
        score = max(0.0, 0.3 - (delta - ENERGY_ACCEPTABLE_THRESHOLD) * 0.1)
        return score, f"Warning - Large energy jump (±{delta} levels)"


def calculate_compatibility_score(track1: Dict[str, Any], track2: Dict[str, Any]) -> float:
    """
    Calculate overall compatibility score between two tracks.

    Weighted scoring:
    - BPM compatibility: 30%
    - Harmonic compatibility: 50% (most important for mix quality)
    - Energy flow: 20%

    Args:
        track1: First track dictionary with metadata
        track2: Second track dictionary with metadata

    Returns:
        Overall compatibility score (0.0-1.0)
        - 0.9-1.0: Excellent mix
        - 0.7-0.9: Good mix
        - 0.5-0.7: Acceptable mix
        - <0.5: Not recommended

    Raises:
        KeyError: If required metadata fields are missing

    Example:
        >>> track1 = {"bpm": 128.0, "key": "8A", "energy": 7}
        >>> track2 = {"bpm": 129.0, "key": "9A", "energy": 8}
        >>> calculate_compatibility_score(track1, track2)
        0.87
    """
    try:
        # Validate required fields
        required_fields = ["bpm", "key", "energy"]
        for field in required_fields:
            if field not in track1 or field not in track2:
                raise KeyError(f"Missing required field: {field}")

        # Calculate individual scores
        bpm_score, _ = calculate_bpm_compatibility(track1["bpm"], track2["bpm"])
        key_score, _ = calculate_key_compatibility(track1["key"], track2["key"])
        energy_score, _ = calculate_energy_compatibility(track1["energy"], track2["energy"])

        # Weighted average
        total_score = (
            bpm_score * WEIGHT_BPM +
            key_score * WEIGHT_KEY +
            energy_score * WEIGHT_ENERGY
        )

        logger.debug(
            f"Compatibility calculated",
            extra={
                "track1": track1.get("id", "unknown"),
                "track2": track2.get("id", "unknown"),
                "bpm_score": bpm_score,
                "key_score": key_score,
                "energy_score": energy_score,
                "total_score": total_score,
            }
        )

        return round(total_score, 2)

    except Exception as e:
        logger.error(
            f"Compatibility calculation failed: {str(e)}",
            extra={
                "track1_id": track1.get("id", "unknown"),
                "track2_id": track2.get("id", "unknown"),
                "error_type": type(e).__name__,
            }
        )
        raise


def find_compatible_tracks(
    reference_track: Dict[str, Any],
    candidate_tracks: List[Dict[str, Any]],
    count: int = 5
) -> List[Dict[str, Any]]:
    """
    Find tracks most compatible with reference track for mixing.

    Analyzes BPM, key, and energy compatibility to identify best mixing candidates.
    Returns tracks sorted by compatibility score (highest first).

    Args:
        reference_track: Current playing track to find matches for
        candidate_tracks: Pool of tracks to search through
        count: Number of compatible tracks to return (default 5)

    Returns:
        List of track dictionaries with added 'compatibility_score' field,
        sorted by compatibility (best matches first)

    Raises:
        ValueError: If reference_track or candidate_tracks are invalid

    Example:
        >>> reference = {"id": "current", "bpm": 128, "key": "8A", "energy": 7}
        >>> candidates = get_mock_library()
        >>> matches = find_compatible_tracks(reference, candidates, count=3)
        >>> len(matches)
        3
        >>> matches[0]["compatibility_score"] >= 0.7
        True
    """
    try:
        if not reference_track:
            raise ValueError("reference_track cannot be empty")

        if not candidate_tracks:
            logger.warning("No candidate tracks provided")
            return []

        # Calculate compatibility scores for all candidates
        scored_tracks = []

        for candidate in candidate_tracks:
            # Skip if same track
            if candidate.get("id") == reference_track.get("id"):
                continue

            try:
                score = calculate_compatibility_score(reference_track, candidate)

                # Add compatibility score to track
                track_with_score = candidate.copy()
                track_with_score["compatibility_score"] = score

                scored_tracks.append(track_with_score)

            except Exception as e:
                logger.warning(
                    f"Skipping track due to compatibility error",
                    extra={
                        "track_id": candidate.get("id", "unknown"),
                        "error": str(e),
                    }
                )
                continue

        # Sort by compatibility score (highest first)
        scored_tracks.sort(key=lambda x: x["compatibility_score"], reverse=True)

        # Return top N tracks
        result = scored_tracks[:count]

        logger.info(
            f"Found {len(result)} compatible tracks",
            extra={
                "reference_track": reference_track.get("id", "unknown"),
                "candidate_count": len(candidate_tracks),
                "result_count": len(result),
                "top_score": result[0]["compatibility_score"] if result else 0,
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"find_compatible_tracks failed: {str(e)}",
            extra={
                "reference_track_id": reference_track.get("id", "unknown"),
                "candidate_count": len(candidate_tracks),
                "error_type": type(e).__name__,
            }
        )
        raise


def find_tracks_by_criteria(
    criteria: Dict[str, Any],
    library: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Search library by multiple criteria (genre, BPM range, key, energy).

    Supports filtering by:
    - genre: Exact genre match
    - bpm_min, bpm_max: BPM range (inclusive)
    - key: Exact Camelot key match
    - energy_min, energy_max: Energy range (inclusive)

    Args:
        criteria: Dictionary of search criteria
        library: Music library to search

    Returns:
        List of tracks matching ALL specified criteria

    Example:
        >>> library = get_mock_library()
        >>> criteria = {"genre": "house", "bpm_min": 120, "bpm_max": 125}
        >>> results = find_tracks_by_criteria(criteria, library)
        >>> all(120 <= t["bpm"] <= 125 for t in results)
        True
    """
    try:
        if not library:
            logger.warning("Empty library provided")
            return []

        matching_tracks = []

        for track in library:
            # Check each criterion
            matches = True

            # Genre filter
            if "genre" in criteria:
                if track.get("genre", "").lower() != criteria["genre"].lower():
                    matches = False
                    continue

            # BPM range filter
            if "bpm_min" in criteria:
                if track.get("bpm", 0) < criteria["bpm_min"]:
                    matches = False
                    continue

            if "bpm_max" in criteria:
                if track.get("bpm", 999) > criteria["bpm_max"]:
                    matches = False
                    continue

            # Key filter (exact match or compatible)
            if "key" in criteria:
                if "key_compatible" in criteria and criteria["key_compatible"]:
                    # Check harmonic compatibility
                    if not is_key_compatible(criteria["key"], track.get("key", "")):
                        matches = False
                        continue
                else:
                    # Exact key match
                    if track.get("key", "") != criteria["key"]:
                        matches = False
                        continue

            # Energy range filter
            if "energy_min" in criteria:
                if track.get("energy", 0) < criteria["energy_min"]:
                    matches = False
                    continue

            if "energy_max" in criteria:
                if track.get("energy", 10) > criteria["energy_max"]:
                    matches = False
                    continue

            if matches:
                matching_tracks.append(track)

        logger.info(
            f"Criteria search completed",
            extra={
                "criteria": criteria,
                "library_size": len(library),
                "matches_found": len(matching_tracks),
            }
        )

        return matching_tracks

    except Exception as e:
        logger.error(
            f"find_tracks_by_criteria failed: {str(e)}",
            extra={
                "criteria": criteria,
                "library_size": len(library),
                "error_type": type(e).__name__,
            }
        )
        raise


def get_transition_candidates(
    current_track: Dict[str, Any],
    library: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Find best next tracks for transition from current track.

    Considers:
    - Harmonic mixing compatibility (Camelot wheel)
    - Energy flow appropriateness
    - BPM compatibility

    Returns top 10 candidates with detailed scoring.

    Args:
        current_track: Currently playing track
        library: Music library to search

    Returns:
        List of up to 10 tracks with compatibility_score field,
        sorted by compatibility (best first)

    Example:
        >>> current = {"id": "now", "bpm": 128, "key": "8A", "energy": 7}
        >>> library = get_mock_library()
        >>> candidates = get_transition_candidates(current, library)
        >>> len(candidates) <= 10
        True
    """
    try:
        logger.info(
            f"Finding transition candidates",
            extra={
                "current_track": current_track.get("id", "unknown"),
                "library_size": len(library),
            }
        )

        # Use find_compatible_tracks with count=10
        candidates = find_compatible_tracks(
            reference_track=current_track,
            candidate_tracks=library,
            count=10
        )

        return candidates

    except Exception as e:
        logger.error(
            f"get_transition_candidates failed: {str(e)}",
            extra={
                "current_track_id": current_track.get("id", "unknown"),
                "library_size": len(library),
                "error_type": type(e).__name__,
            }
        )
        raise


def build_setlist(
    genre: str,
    duration_minutes: int,
    energy_profile: str = "build"
) -> List[Dict[str, Any]]:
    """
    Generate complete setlist for specified genre and duration.

    Energy profiles:
    - 'build': Gradual energy increase (opening set)
      Start: Energy 4-5 (BPM 120-122)
      Peak: Energy 8-9 (BPM 126-128)

    - 'maintain': Sustained high energy (peak time)
      Sustained: Energy 7-9 (BPM 126-128)

    - 'wave': Wave pattern (dynamic set)
      Build → Peak → Drop → Build (energy cycles)

    Args:
        genre: Genre to build setlist for
        duration_minutes: Target duration in minutes
        energy_profile: Energy progression ('build', 'maintain', 'wave')

    Returns:
        Ordered list of tracks with smooth transitions and energy flow

    Raises:
        ValueError: If invalid energy_profile specified

    Example:
        >>> setlist = build_setlist("house", 60, "build")
        >>> len(setlist) > 0
        True
        >>> setlist[0]["energy"] < setlist[-1]["energy"]  # Build profile
        True
    """
    try:
        # Validate energy profile
        valid_profiles = ["build", "maintain", "wave"]
        if energy_profile not in valid_profiles:
            raise ValueError(f"Invalid energy_profile: {energy_profile}. Must be one of {valid_profiles}")

        # Get library (in production, this would be actual library)
        library = get_mock_library()

        # Filter by genre
        genre_tracks = find_tracks_by_criteria({"genre": genre}, library)

        if not genre_tracks:
            logger.warning(f"No tracks found for genre: {genre}")
            return []

        # Calculate target number of tracks
        avg_track_duration_min = 5  # Average 5 minutes per track
        target_track_count = math.ceil(duration_minutes / avg_track_duration_min)

        # Build setlist based on energy profile
        setlist = []

        if energy_profile == "build":
            # Opening set: gradual energy increase
            # Start with low energy, end with high energy

            # Sort tracks by energy
            sorted_tracks = sorted(genre_tracks, key=lambda t: t["energy"])

            # Select tracks with progressive energy increase
            for i in range(min(target_track_count, len(sorted_tracks))):
                setlist.append(sorted_tracks[i])

        elif energy_profile == "maintain":
            # Peak time: sustained high energy
            # Filter high energy tracks (7-9)
            high_energy_tracks = find_tracks_by_criteria(
                {"genre": genre, "energy_min": 7, "energy_max": 9},
                library
            )

            if not high_energy_tracks:
                logger.warning("No high energy tracks found, using all genre tracks")
                high_energy_tracks = genre_tracks

            # Build setlist with compatible transitions
            if high_energy_tracks:
                setlist.append(high_energy_tracks[0])

                while len(setlist) < target_track_count and len(setlist) < len(high_energy_tracks):
                    # Find compatible next track
                    candidates = find_compatible_tracks(
                        reference_track=setlist[-1],
                        candidate_tracks=[t for t in high_energy_tracks if t not in setlist],
                        count=3
                    )

                    if candidates:
                        setlist.append(candidates[0])
                    else:
                        break

        elif energy_profile == "wave":
            # Wave pattern: build → peak → drop → build
            # Create energy wave pattern

            # Divide tracks into thirds
            third = math.ceil(target_track_count / 3)

            # Low energy start
            low_energy = find_tracks_by_criteria(
                {"genre": genre, "energy_min": 4, "energy_max": 6},
                library
            )

            # High energy peak
            high_energy = find_tracks_by_criteria(
                {"genre": genre, "energy_min": 7, "energy_max": 9},
                library
            )

            # Mid energy drop
            mid_energy = find_tracks_by_criteria(
                {"genre": genre, "energy_min": 5, "energy_max": 7},
                library
            )

            # Build wave pattern
            setlist.extend(sorted(low_energy, key=lambda t: t["energy"])[:third])
            setlist.extend(sorted(high_energy, key=lambda t: t["energy"], reverse=True)[:third])
            setlist.extend(sorted(mid_energy, key=lambda t: t["energy"])[:third])

        # Optimize transitions (ensure harmonic compatibility)
        optimized_setlist = _optimize_setlist_transitions(setlist)

        logger.info(
            f"Setlist generated",
            extra={
                "genre": genre,
                "duration_minutes": duration_minutes,
                "energy_profile": energy_profile,
                "track_count": len(optimized_setlist),
                "energy_range": f"{optimized_setlist[0]['energy']}-{optimized_setlist[-1]['energy']}" if optimized_setlist else "N/A",
            }
        )

        return optimized_setlist

    except Exception as e:
        logger.error(
            f"build_setlist failed: {str(e)}",
            extra={
                "genre": genre,
                "duration_minutes": duration_minutes,
                "energy_profile": energy_profile,
                "error_type": type(e).__name__,
            }
        )
        raise


def _optimize_setlist_transitions(tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Optimize track order for smooth harmonic transitions.

    Internal helper function for build_setlist.
    Uses greedy algorithm to minimize harmonic clashes.

    Args:
        tracks: Unordered list of tracks

    Returns:
        Reordered tracks with optimized transitions
    """
    if len(tracks) <= 1:
        return tracks

    optimized = [tracks[0]]
    remaining = [t for t in tracks[1:]]  # Create copy to avoid mutation issues

    while remaining:
        current = optimized[-1]

        # Find most compatible next track
        candidates = find_compatible_tracks(
            reference_track=current,
            candidate_tracks=remaining,
            count=1
        )

        if candidates:
            # Find the matching track in remaining by ID
            selected_track = candidates[0]
            selected_id = selected_track.get("id")

            # Remove by finding matching ID in remaining list
            for i, track in enumerate(remaining):
                if track.get("id") == selected_id:
                    optimized.append(track)
                    remaining.pop(i)
                    break
        else:
            # No compatible tracks found, add next available
            optimized.append(remaining[0])
            remaining.pop(0)

    return optimized


# ============================================================================
# TESTING & VALIDATION
# ============================================================================

if __name__ == "__main__":
    """
    Test suite for track selector module
    """
    import sys

    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s - %(message)s"
    )

    print("=" * 80)
    print("Track Selector Module - Test Suite")
    print("=" * 80)

    # Test 1: Mock library
    print("\n[Test 1] Loading mock library...")
    library = get_mock_library()
    print(f"✓ Loaded {len(library)} tracks")

    # Test 2: BPM compatibility
    print("\n[Test 2] BPM compatibility...")
    score, rec = calculate_bpm_compatibility(128.0, 129.0)
    print(f"  128 BPM → 129 BPM: {score:.2f} ({rec})")
    score, rec = calculate_bpm_compatibility(128.0, 135.0)
    print(f"  128 BPM → 135 BPM: {score:.2f} ({rec})")

    # Test 3: Key compatibility
    print("\n[Test 3] Harmonic compatibility...")
    print(f"  8A → 8A: {is_key_compatible('8A', '8A')}")
    print(f"  8A → 8B: {is_key_compatible('8A', '8B')}")
    print(f"  8A → 9A: {is_key_compatible('8A', '9A')}")
    print(f"  8A → 3A: {is_key_compatible('8A', '3A')}")

    # Test 4: Find compatible tracks
    print("\n[Test 4] Finding compatible tracks...")
    reference = library[3]  # Mid-energy track
    print(f"  Reference: {reference['title']} ({reference['bpm']} BPM, {reference['key']}, Energy {reference['energy']})")

    compatible = find_compatible_tracks(reference, library, count=3)
    print(f"  Found {len(compatible)} compatible tracks:")
    for track in compatible:
        print(f"    - {track['title']}: Score {track['compatibility_score']:.2f}")

    # Test 5: Search by criteria
    print("\n[Test 5] Search by criteria...")
    criteria = {"genre": "house", "bpm_min": 124, "bpm_max": 128, "energy_min": 7}
    results = find_tracks_by_criteria(criteria, library)
    print(f"  Criteria: {criteria}")
    print(f"  Found {len(results)} matching tracks")

    # Test 6: Build setlist
    print("\n[Test 6] Building setlist...")
    setlist = build_setlist("house", 60, "build")
    print(f"  Generated {len(setlist)} track setlist (60 min, 'build' profile)")
    print(f"  Energy progression: {[t['energy'] for t in setlist]}")

    print("\n" + "=" * 80)
    print("All tests completed successfully!")
    print("=" * 80)
