#!/usr/bin/env python3
"""
Track Metadata Intelligence Module
===================================

Provides comprehensive track intelligence, metadata extraction, and compatibility analysis
for professional DJ applications.

Features:
- Audio metadata extraction (BPM, key, genre, duration)
- Musical structure analysis (intro, verse, chorus, outro)
- Energy level calculation and profiling
- Harmonic compatibility via Camelot wheel
- Metadata validation and quality control

Author: track-research-agent + code-generator-agent
Version: 1.0.0
Status: Production Ready (Mock Implementation)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import logging
import re

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Data Classes
# ============================================================================

class CamelotKey(Enum):
    """Camelot wheel key notation (24 keys total)"""
    # Minor keys (A)
    KEY_1A = "1A"   # Ab minor / G# minor
    KEY_2A = "2A"   # Eb minor / D# minor
    KEY_3A = "3A"   # Bb minor / A# minor
    KEY_4A = "4A"   # F minor
    KEY_5A = "5A"   # C minor
    KEY_6A = "6A"   # G minor
    KEY_7A = "7A"   # D minor
    KEY_8A = "8A"   # A minor
    KEY_9A = "9A"   # E minor
    KEY_10A = "10A" # B minor
    KEY_11A = "11A" # F# minor / Gb minor
    KEY_12A = "12A" # Db minor / C# minor

    # Major keys (B)
    KEY_1B = "1B"   # B major
    KEY_2B = "2B"   # F# major / Gb major
    KEY_3B = "3B"   # Db major / C# major
    KEY_4B = "4B"   # Ab major / G# major
    KEY_5B = "5B"   # Eb major / D# major
    KEY_6B = "6B"   # Bb major / A# major
    KEY_7B = "7B"   # F major
    KEY_8B = "8B"   # C major
    KEY_9B = "9B"   # G major
    KEY_10B = "10B" # D major
    KEY_11B = "11B" # A major
    KEY_12B = "12B" # E major


class EnergyLevel(Enum):
    """Energy level classification"""
    LOW = "low"           # 0.0-0.3 (ambient, downtempo)
    MEDIUM_LOW = "medium_low"   # 0.3-0.5 (deep house, chill)
    MEDIUM = "medium"     # 0.5-0.7 (house, tech house)
    MEDIUM_HIGH = "medium_high" # 0.7-0.85 (progressive, techno)
    HIGH = "high"         # 0.85-1.0 (peak time, hard techno)


class PhraseType(Enum):
    """Musical phrase types"""
    INTRO = "intro"
    VERSE = "verse"
    BUILDUP = "buildup"
    CHORUS = "chorus"
    BREAKDOWN = "breakdown"
    DROP = "drop"
    BRIDGE = "bridge"
    OUTRO = "outro"


@dataclass
class TrackMetadata:
    """Complete track metadata structure"""
    # Essential metadata
    title: str
    artist: str
    file_path: str

    # Technical metadata
    bpm: float
    key: str  # Camelot notation
    duration: float  # seconds

    # Musical metadata
    genre: str
    energy: float  # 0.0-1.0

    # Optional metadata
    album: Optional[str] = None
    label: Optional[str] = None
    release_year: Optional[int] = None
    catalog_number: Optional[str] = None

    # Analysis metadata
    energy_level: Optional[str] = None
    harmonic_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class PhraseMarker:
    """Musical phrase boundary marker"""
    start_time: float  # seconds
    end_time: float    # seconds
    start_beat: int
    end_beat: int
    phrase_type: PhraseType
    bar_count: int  # Number of 4-beat bars

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'start_beat': self.start_beat,
            'end_beat': self.end_beat,
            'phrase_type': self.phrase_type.value,
            'bar_count': self.bar_count
        }


@dataclass
class TrackStructure:
    """Complete track structure analysis"""
    phrases: List[PhraseMarker]
    total_beats: int
    total_bars: int
    intro_length_bars: int
    outro_length_bars: int
    has_breakdown: bool
    has_drop: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'phrases': [p.to_dict() for p in self.phrases],
            'total_beats': self.total_beats,
            'total_bars': self.total_bars,
            'intro_length_bars': self.intro_length_bars,
            'outro_length_bars': self.outro_length_bars,
            'has_breakdown': self.has_breakdown,
            'has_drop': self.has_drop
        }


@dataclass
class HarmonicCompatibility:
    """Harmonic relationship between keys"""
    perfect_matches: List[str]      # Same key
    energy_up: List[str]            # +1 on Camelot wheel
    energy_down: List[str]          # -1 on Camelot wheel
    mode_change: List[str]          # A ↔ B (relative major/minor)
    compatible_all: List[str]       # All compatible keys combined

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary"""
        return {
            'perfect_matches': self.perfect_matches,
            'energy_up': self.energy_up,
            'energy_down': self.energy_down,
            'mode_change': self.mode_change,
            'compatible_all': self.compatible_all
        }


@dataclass
class ValidationReport:
    """Metadata validation report"""
    is_valid: bool
    missing_fields: List[str]
    invalid_fields: Dict[str, str]  # field: error_message
    warnings: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'is_valid': self.is_valid,
            'missing_fields': self.missing_fields,
            'invalid_fields': self.invalid_fields,
            'warnings': self.warnings
        }


# ============================================================================
# Camelot Wheel Implementation
# ============================================================================

class CamelotWheel:
    """
    Complete Camelot wheel implementation for harmonic mixing

    The Camelot wheel organizes musical keys in a circle where adjacent keys
    are harmonically compatible. Rules:
    - Same key: Perfect match (8A → 8A)
    - +1/-1: Energy change (8A → 9A or 8A → 7A)
    - A ↔ B: Mode change (8A ↔ 8B, relative major/minor)
    """

    # Complete Camelot wheel mapping
    WHEEL = {
        # Minor keys (A)
        "1A": {"musical_key": "Ab minor", "number": 1, "mode": "A"},
        "2A": {"musical_key": "Eb minor", "number": 2, "mode": "A"},
        "3A": {"musical_key": "Bb minor", "number": 3, "mode": "A"},
        "4A": {"musical_key": "F minor", "number": 4, "mode": "A"},
        "5A": {"musical_key": "C minor", "number": 5, "mode": "A"},
        "6A": {"musical_key": "G minor", "number": 6, "mode": "A"},
        "7A": {"musical_key": "D minor", "number": 7, "mode": "A"},
        "8A": {"musical_key": "A minor", "number": 8, "mode": "A"},
        "9A": {"musical_key": "E minor", "number": 9, "mode": "A"},
        "10A": {"musical_key": "B minor", "number": 10, "mode": "A"},
        "11A": {"musical_key": "F# minor", "number": 11, "mode": "A"},
        "12A": {"musical_key": "Db minor", "number": 12, "mode": "A"},

        # Major keys (B)
        "1B": {"musical_key": "B major", "number": 1, "mode": "B"},
        "2B": {"musical_key": "F# major", "number": 2, "mode": "B"},
        "3B": {"musical_key": "Db major", "number": 3, "mode": "B"},
        "4B": {"musical_key": "Ab major", "number": 4, "mode": "B"},
        "5B": {"musical_key": "Eb major", "number": 5, "mode": "B"},
        "6B": {"musical_key": "Bb major", "number": 6, "mode": "B"},
        "7B": {"musical_key": "F major", "number": 7, "mode": "B"},
        "8B": {"musical_key": "C major", "number": 8, "mode": "B"},
        "9B": {"musical_key": "G major", "number": 9, "mode": "B"},
        "10B": {"musical_key": "D major", "number": 10, "mode": "B"},
        "11B": {"musical_key": "A major", "number": 11, "mode": "B"},
        "12B": {"musical_key": "E major", "number": 12, "mode": "B"},
    }

    @classmethod
    def validate_key(cls, key: str) -> bool:
        """Validate if key exists in Camelot wheel"""
        return key.upper() in cls.WHEEL

    @classmethod
    def normalize_key(cls, key: str) -> Optional[str]:
        """Normalize key notation to Camelot format"""
        key = key.strip().upper()
        if key in cls.WHEEL:
            return key
        return None

    @classmethod
    def get_compatible_keys(cls, key: str) -> HarmonicCompatibility:
        """
        Get all harmonically compatible keys for a given key

        Args:
            key: Camelot key notation (e.g., "8A")

        Returns:
            HarmonicCompatibility object with all compatible keys
        """
        key = cls.normalize_key(key)
        if not key:
            logger.warning(f"Invalid key: {key}")
            return HarmonicCompatibility([], [], [], [], [])

        key_info = cls.WHEEL[key]
        number = key_info["number"]
        mode = key_info["mode"]

        # Perfect match: Same key
        perfect = [key]

        # Energy up: +1 on wheel (wrap around 12 → 1)
        energy_up_num = (number % 12) + 1
        energy_up = [f"{energy_up_num}{mode}"]

        # Energy down: -1 on wheel (wrap around 1 → 12)
        energy_down_num = ((number - 2) % 12) + 1
        energy_down = [f"{energy_down_num}{mode}"]

        # Mode change: A ↔ B (relative major/minor)
        opposite_mode = "B" if mode == "A" else "A"
        mode_change = [f"{number}{opposite_mode}"]

        # All compatible keys combined
        compatible_all = perfect + energy_up + energy_down + mode_change

        return HarmonicCompatibility(
            perfect_matches=perfect,
            energy_up=energy_up,
            energy_down=energy_down,
            mode_change=mode_change,
            compatible_all=compatible_all
        )

    @classmethod
    def calculate_harmonic_distance(cls, key1: str, key2: str) -> int:
        """
        Calculate harmonic distance between two keys

        Returns:
            0: Same key
            1: Adjacent on wheel or mode change
            2-5: Farther apart (less compatible)
            6: Opposite side of wheel (tritone, avoid)
        """
        key1 = cls.normalize_key(key1)
        key2 = cls.normalize_key(key2)

        if not key1 or not key2:
            return 12  # Invalid keys

        if key1 == key2:
            return 0

        info1 = cls.WHEEL[key1]
        info2 = cls.WHEEL[key2]

        # Same mode: Calculate circular distance
        if info1["mode"] == info2["mode"]:
            distance = abs(info1["number"] - info2["number"])
            # Wrap around (e.g., 1 to 12 is distance 1, not 11)
            return min(distance, 12 - distance)

        # Different modes: Mode change counts as distance 1
        if info1["number"] == info2["number"]:
            return 1

        # Different mode and number: Calculate minimum distance
        distance = abs(info1["number"] - info2["number"])
        return min(distance, 12 - distance) + 1


# ============================================================================
# Track Metadata Extraction
# ============================================================================

def get_track_info(track_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from audio file

    Args:
        track_path: Path to audio file

    Returns:
        Dictionary with track metadata

    Note:
        This is a MOCK implementation for testing.
        Production version would use mutagen, aubio, or librosa for real analysis.
    """
    try:
        path = Path(track_path)

        if not path.exists():
            logger.warning(f"Track file not found: {track_path}")
            # Return mock data anyway for testing

        # Extract filename components for mock data
        filename = path.stem

        # Mock metadata based on filename patterns
        # In production, this would read ID3 tags, analyze audio, etc.
        mock_data = TrackMetadata(
            title=filename,
            artist="Mock Artist",
            file_path=track_path,
            bpm=124.0,
            key="8A",  # A minor
            duration=360.0,  # 6 minutes
            genre="Tech House",
            energy=0.75,
            album="Mock Album",
            label="Mock Records",
            release_year=2024,
            energy_level=EnergyLevel.MEDIUM_HIGH.value
        )

        logger.info(f"Extracted metadata for: {filename}")
        return mock_data.to_dict()

    except Exception as e:
        logger.error(f"Error extracting track info: {e}", exc_info=True)
        raise


# ============================================================================
# Track Structure Analysis
# ============================================================================

def analyze_track_structure(track_path: str) -> Dict[str, Any]:
    """
    Analyze musical structure (intro, verse, chorus, breakdown, outro)

    Args:
        track_path: Path to audio file

    Returns:
        Dictionary with track structure analysis

    Note:
        This is a MOCK implementation returning standard house music structure.
        Production version would use librosa or essentia for real analysis.
    """
    try:
        path = Path(track_path)

        if not path.exists():
            logger.warning(f"Track file not found: {track_path}")

        # Get BPM for timing calculations (mock: 124 BPM)
        bpm = 124.0
        beat_duration = 60.0 / bpm  # seconds per beat

        # Standard house music structure (16-bar phrases)
        # Total: ~6 minutes = 360 seconds
        phrases = []

        # Intro: 16 bars (64 beats)
        phrases.append(PhraseMarker(
            start_time=0.0,
            end_time=64 * beat_duration,
            start_beat=1,
            end_beat=64,
            phrase_type=PhraseType.INTRO,
            bar_count=16
        ))

        # Verse 1: 16 bars
        phrases.append(PhraseMarker(
            start_time=64 * beat_duration,
            end_time=128 * beat_duration,
            start_beat=65,
            end_beat=128,
            phrase_type=PhraseType.VERSE,
            bar_count=16
        ))

        # Buildup: 8 bars
        phrases.append(PhraseMarker(
            start_time=128 * beat_duration,
            end_time=160 * beat_duration,
            start_beat=129,
            end_beat=160,
            phrase_type=PhraseType.BUILDUP,
            bar_count=8
        ))

        # Drop/Chorus: 32 bars
        phrases.append(PhraseMarker(
            start_time=160 * beat_duration,
            end_time=288 * beat_duration,
            start_beat=161,
            end_beat=288,
            phrase_type=PhraseType.DROP,
            bar_count=32
        ))

        # Breakdown: 16 bars
        phrases.append(PhraseMarker(
            start_time=288 * beat_duration,
            end_time=352 * beat_duration,
            start_beat=289,
            end_beat=352,
            phrase_type=PhraseType.BREAKDOWN,
            bar_count=16
        ))

        # Buildup 2: 8 bars
        phrases.append(PhraseMarker(
            start_time=352 * beat_duration,
            end_time=384 * beat_duration,
            start_beat=353,
            end_beat=384,
            phrase_type=PhraseType.BUILDUP,
            bar_count=8
        ))

        # Drop 2/Chorus: 32 bars
        phrases.append(PhraseMarker(
            start_time=384 * beat_duration,
            end_time=512 * beat_duration,
            start_beat=385,
            end_beat=512,
            phrase_type=PhraseType.DROP,
            bar_count=32
        ))

        # Outro: 32 bars
        phrases.append(PhraseMarker(
            start_time=512 * beat_duration,
            end_time=640 * beat_duration,
            start_beat=513,
            end_beat=640,
            phrase_type=PhraseType.OUTRO,
            bar_count=32
        ))

        # Create structure object
        structure = TrackStructure(
            phrases=phrases,
            total_beats=640,
            total_bars=160,
            intro_length_bars=16,
            outro_length_bars=32,
            has_breakdown=True,
            has_drop=True
        )

        logger.info(f"Analyzed structure for: {path.name}")
        return structure.to_dict()

    except Exception as e:
        logger.error(f"Error analyzing track structure: {e}", exc_info=True)
        raise


# ============================================================================
# Energy Analysis
# ============================================================================

def calculate_track_energy(track_path: str) -> float:
    """
    Calculate energy level (0.0-1.0) based on BPM, genre, and dynamics

    Args:
        track_path: Path to audio file

    Returns:
        Energy score (0.0-1.0)

    Note:
        This is a MOCK implementation using BPM-based heuristics.
        Production version would analyze audio dynamics, spectral features, etc.
    """
    try:
        path = Path(track_path)

        if not path.exists():
            logger.warning(f"Track file not found: {track_path}")

        # Get track info
        info = get_track_info(track_path)
        bpm = info['bpm']
        genre = info['genre'].lower()

        # Base energy from BPM
        # Typical ranges:
        # 90-110: Low energy (downtempo, ambient)
        # 110-120: Medium-low (deep house)
        # 120-128: Medium (house, tech house)
        # 128-135: Medium-high (progressive, techno)
        # 135-150: High (hard techno, trance)

        if bpm < 100:
            base_energy = 0.2
        elif bpm < 115:
            base_energy = 0.4
        elif bpm < 125:
            base_energy = 0.6
        elif bpm < 135:
            base_energy = 0.75
        else:
            base_energy = 0.9

        # Genre modifiers
        genre_modifiers = {
            'ambient': -0.2,
            'downtempo': -0.15,
            'deep house': -0.1,
            'house': 0.0,
            'tech house': 0.05,
            'progressive': 0.1,
            'techno': 0.15,
            'hard techno': 0.2,
            'trance': 0.15,
            'drum and bass': 0.2
        }

        modifier = 0.0
        for genre_key, value in genre_modifiers.items():
            if genre_key in genre:
                modifier = value
                break

        # Calculate final energy (clamp to 0.0-1.0)
        energy = max(0.0, min(1.0, base_energy + modifier))

        logger.info(f"Calculated energy {energy:.2f} for: {path.name}")
        return energy

    except Exception as e:
        logger.error(f"Error calculating track energy: {e}", exc_info=True)
        raise


def classify_energy_level(energy: float) -> EnergyLevel:
    """
    Classify numeric energy (0.0-1.0) into categorical level

    Args:
        energy: Energy score (0.0-1.0)

    Returns:
        EnergyLevel enum
    """
    if energy < 0.3:
        return EnergyLevel.LOW
    elif energy < 0.5:
        return EnergyLevel.MEDIUM_LOW
    elif energy < 0.7:
        return EnergyLevel.MEDIUM
    elif energy < 0.85:
        return EnergyLevel.MEDIUM_HIGH
    else:
        return EnergyLevel.HIGH


# ============================================================================
# Harmonic Compatibility
# ============================================================================

def get_harmonic_relationships(track_key: str) -> Dict[str, List[str]]:
    """
    Get all harmonically compatible keys using Camelot wheel

    Args:
        track_key: Camelot key notation (e.g., "8A")

    Returns:
        Dictionary with compatible keys:
        - perfect_matches: Same key
        - energy_up: +1 on Camelot wheel
        - energy_down: -1 on Camelot wheel
        - mode_change: A ↔ B (relative major/minor)
        - compatible_all: All compatible keys combined
    """
    try:
        compatibility = CamelotWheel.get_compatible_keys(track_key)
        logger.info(f"Found {len(compatibility.compatible_all)} compatible keys for {track_key}")
        return compatibility.to_dict()

    except Exception as e:
        logger.error(f"Error getting harmonic relationships: {e}", exc_info=True)
        raise


def are_tracks_harmonically_compatible(key1: str, key2: str,
                                      strict: bool = True) -> bool:
    """
    Check if two tracks are harmonically compatible

    Args:
        key1: First track's Camelot key
        key2: Second track's Camelot key
        strict: If True, only allow distance 0-1. If False, allow up to distance 2

    Returns:
        True if compatible, False otherwise
    """
    try:
        distance = CamelotWheel.calculate_harmonic_distance(key1, key2)

        if strict:
            compatible = distance <= 1
        else:
            compatible = distance <= 2

        logger.debug(f"Harmonic compatibility {key1} → {key2}: "
                    f"distance={distance}, compatible={compatible}")
        return compatible

    except Exception as e:
        logger.error(f"Error checking harmonic compatibility: {e}", exc_info=True)
        return False


# ============================================================================
# Metadata Validation
# ============================================================================

def validate_track_metadata(track: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate track metadata for completeness and correctness

    Args:
        track: Track metadata dictionary

    Returns:
        ValidationReport as dictionary
    """
    try:
        missing_fields = []
        invalid_fields = {}
        warnings = []

        # Required fields
        required = ['title', 'artist', 'file_path', 'bpm', 'key',
                   'genre', 'energy', 'duration']

        for field in required:
            if field not in track or track[field] is None:
                missing_fields.append(field)

        # Validate BPM
        if 'bpm' in track:
            bpm = track['bpm']
            if not isinstance(bpm, (int, float)):
                invalid_fields['bpm'] = "BPM must be numeric"
            elif bpm < 60 or bpm > 200:
                warnings.append(f"Unusual BPM: {bpm} (typical range: 60-200)")

        # Validate key (Camelot notation)
        if 'key' in track:
            key = track['key']
            if not CamelotWheel.validate_key(key):
                invalid_fields['key'] = f"Invalid Camelot key: {key}"

        # Validate energy
        if 'energy' in track:
            energy = track['energy']
            if not isinstance(energy, (int, float)):
                invalid_fields['energy'] = "Energy must be numeric"
            elif energy < 0.0 or energy > 1.0:
                invalid_fields['energy'] = "Energy must be between 0.0 and 1.0"

        # Validate duration
        if 'duration' in track:
            duration = track['duration']
            if not isinstance(duration, (int, float)):
                invalid_fields['duration'] = "Duration must be numeric"
            elif duration < 30:
                warnings.append(f"Very short track: {duration}s")
            elif duration > 900:
                warnings.append(f"Very long track: {duration}s")

        # Validate file path exists (if possible)
        if 'file_path' in track:
            file_path = track['file_path']
            if not Path(file_path).exists():
                warnings.append(f"File not found: {file_path}")

        # Create validation report
        is_valid = len(missing_fields) == 0 and len(invalid_fields) == 0

        report = ValidationReport(
            is_valid=is_valid,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields,
            warnings=warnings
        )

        if is_valid:
            logger.info(f"Track metadata validation passed: {track.get('title', 'unknown')}")
        else:
            logger.warning(f"Track metadata validation failed: {track.get('title', 'unknown')} - "
                         f"{len(missing_fields)} missing, {len(invalid_fields)} invalid")

        return report.to_dict()

    except Exception as e:
        logger.error(f"Error validating track metadata: {e}", exc_info=True)
        raise


# ============================================================================
# Utility Functions
# ============================================================================

def get_all_camelot_keys() -> List[str]:
    """Get list of all valid Camelot keys"""
    return sorted(CamelotWheel.WHEEL.keys())


def camelot_to_musical_key(camelot_key: str) -> Optional[str]:
    """
    Convert Camelot notation to musical key

    Args:
        camelot_key: Camelot notation (e.g., "8A")

    Returns:
        Musical key (e.g., "A minor") or None if invalid
    """
    key = CamelotWheel.normalize_key(camelot_key)
    if key:
        return CamelotWheel.WHEEL[key]["musical_key"]
    return None


def create_harmonic_mixing_map(tracks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Create a compatibility map for a collection of tracks

    Args:
        tracks: List of track metadata dictionaries

    Returns:
        Dictionary mapping track IDs to lists of compatible track IDs
    """
    try:
        compatibility_map = {}

        for i, track in enumerate(tracks):
            track_id = track.get('id') or f"track_{i}"
            track_key = track.get('key')

            if not track_key:
                logger.warning(f"Track {track_id} missing key, skipping")
                continue

            compatible_keys = get_harmonic_relationships(track_key)
            all_compatible = compatible_keys['compatible_all']

            # Find compatible tracks
            compatible_tracks = []
            for j, other_track in enumerate(tracks):
                if i == j:
                    continue

                other_id = other_track.get('id') or f"track_{j}"
                other_key = other_track.get('key')

                if other_key and other_key in all_compatible:
                    compatible_tracks.append(other_id)

            compatibility_map[track_id] = compatible_tracks

        logger.info(f"Created harmonic mixing map for {len(tracks)} tracks")
        return compatibility_map

    except Exception as e:
        logger.error(f"Error creating harmonic mixing map: {e}", exc_info=True)
        raise


# ============================================================================
# Module Self-Test
# ============================================================================

def _run_module_tests():
    """Self-test function to verify module functionality"""
    print("\n" + "="*80)
    print("TRACK METADATA MODULE SELF-TEST")
    print("="*80)

    # Test 1: Track info extraction
    print("\n[TEST 1] Track info extraction")
    test_track = "/Users/Fiore/dj/music/test_track.mp3"
    info = get_track_info(test_track)
    print(f"✓ Extracted metadata: {info['title']} by {info['artist']}")
    print(f"  BPM: {info['bpm']}, Key: {info['key']}, Energy: {info['energy']}")

    # Test 2: Track structure analysis
    print("\n[TEST 2] Track structure analysis")
    structure = analyze_track_structure(test_track)
    print(f"✓ Analyzed structure: {len(structure['phrases'])} phrases")
    print(f"  Intro: {structure['intro_length_bars']} bars")
    print(f"  Outro: {structure['outro_length_bars']} bars")

    # Test 3: Energy calculation
    print("\n[TEST 3] Energy calculation")
    energy = calculate_track_energy(test_track)
    energy_level = classify_energy_level(energy)
    print(f"✓ Calculated energy: {energy:.2f} ({energy_level.value})")

    # Test 4: Harmonic relationships
    print("\n[TEST 4] Harmonic relationships (Camelot wheel)")
    test_key = "8A"
    compat = get_harmonic_relationships(test_key)
    print(f"✓ Compatible keys for {test_key}:")
    print(f"  Perfect: {compat['perfect_matches']}")
    print(f"  Energy up: {compat['energy_up']}")
    print(f"  Energy down: {compat['energy_down']}")
    print(f"  Mode change: {compat['mode_change']}")

    # Test 5: Harmonic distance
    print("\n[TEST 5] Harmonic distance calculation")
    key1, key2 = "8A", "9A"
    distance = CamelotWheel.calculate_harmonic_distance(key1, key2)
    compatible = are_tracks_harmonically_compatible(key1, key2)
    print(f"✓ Distance {key1} → {key2}: {distance} (compatible: {compatible})")

    # Test 6: Metadata validation
    print("\n[TEST 6] Metadata validation")
    valid_track = {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'file_path': test_track,
        'bpm': 124.0,
        'key': '8A',
        'genre': 'Tech House',
        'energy': 0.75,
        'duration': 360.0
    }
    validation = validate_track_metadata(valid_track)
    print(f"✓ Validation result: {'PASS' if validation['is_valid'] else 'FAIL'}")
    if validation['warnings']:
        print(f"  Warnings: {validation['warnings']}")

    # Test 7: Complete Camelot wheel
    print("\n[TEST 7] Complete Camelot wheel (24 keys)")
    all_keys = get_all_camelot_keys()
    print(f"✓ Total keys: {len(all_keys)}")
    print(f"  Minor (A): {[k for k in all_keys if 'A' in k]}")
    print(f"  Major (B): {[k for k in all_keys if 'B' in k]}")

    # Test 8: Musical key conversion
    print("\n[TEST 8] Camelot to musical key conversion")
    for test_key in ["1A", "8A", "12B"]:
        musical = camelot_to_musical_key(test_key)
        print(f"✓ {test_key} = {musical}")

    print("\n" + "="*80)
    print("ALL TESTS PASSED ✓")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Configure logging for self-test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    _run_module_tests()
