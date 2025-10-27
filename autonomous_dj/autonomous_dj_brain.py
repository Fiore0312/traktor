"""
Autonomous DJ Brain - Decision Making System
Uses OpenRouter LLM for intelligent track selection and mix strategies.
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import sqlite3
import sys
sys.path.append(str(Path(__file__).parent.parent))

from autonomous_dj.openrouter_client import OpenRouterClient
from camelot_matcher import CamelotMatcher


class AutonomousDJBrain:
    """
    AI-powered decision making for autonomous DJ system.
    Handles track selection, mix timing, and energy flow management.
    """

    def __init__(self, openrouter_client: OpenRouterClient = None):
        self.llm = openrouter_client or OpenRouterClient()
        self.camelot = CamelotMatcher()
        self.db_path = Path("tracks.db")
        self.session_history = []

        # Energy level mapping
        self.energy_levels = {
            "low": {"bpm_range": (110, 120), "intensity": "calm"},
            "medium": {"bpm_range": (120, 128), "intensity": "moderate"},
            "high": {"bpm_range": (128, 135), "intensity": "energetic"},
            "peak": {"bpm_range": (135, 145), "intensity": "intense"}
        }

    def decide_next_track(self, current_state: Dict) -> Dict:
        """
        Decide which track to play next based on current state.

        Args:
            current_state: {
                "playing_deck": "A" or "B",
                "current_track": {"bpm": 128, "key": "8A", "genre": "Techno"},
                "energy_level": "medium",
                "genre_preference": "Techno",
                "tracks_played": 5,
                "session_duration_minutes": 30
            }

        Returns: {
            "folder_name": "Techno",
            "track_criteria": {
                "bpm_min": 125,
                "bpm_max": 131,
                "compatible_keys": ["7A", "8A", "8B", "9A"],
                "preferred_track_number": 3
            },
            "reasoning": "Maintaining medium energy, compatible key 8A->8B transition"
        }
        """
        current_track = current_state.get("current_track") or {}  # Handle None case
        energy_level = current_state.get("energy_level", "medium")
        genre = current_state.get("genre_preference", "Techno")

        # Get compatible tracks from database (use defaults if first track)
        current_bpm = current_track.get("bpm", 128) if current_track else 128
        current_key = current_track.get("key", "8A") if current_track else "8A"

        compatible_tracks = self._find_compatible_tracks(
            current_bpm=current_bpm,
            current_key=current_key,
            genre=genre,
            energy_level=energy_level
        )

        if not compatible_tracks:
            # Fallback: use default values
            return self._fallback_track_decision(genre, energy_level)

        # Use LLM to select best track from compatible options
        selected_track = self._llm_select_best_track(
            compatible_tracks,
            current_state
        )

        return selected_track

    def _find_compatible_tracks(self, current_bpm: float, current_key: str,
                                 genre: str, energy_level: str) -> List[Dict]:
        """Query database for harmonically compatible tracks."""
        if not self.db_path.exists():
            return []

        # Camelot Wheel compatible keys
        compatible_keys = self.camelot.get_compatible_keys(current_key)

        # BPM range based on energy level
        energy_config = self.energy_levels.get(energy_level, self.energy_levels["medium"])
        bpm_min = max(current_bpm * 0.94, energy_config["bpm_range"][0])
        bpm_max = min(current_bpm * 1.06, energy_config["bpm_range"][1])

        # Query database
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        query = """
        SELECT path, bpm, camelot
        FROM tracks
        WHERE bpm BETWEEN ? AND ?
        AND camelot IN ({})
        LIMIT 20
        """.format(','.join('?' * len(compatible_keys)))

        params = [bpm_min, bpm_max] + compatible_keys
        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                "file_path": row[0],
                "bpm": row[1],
                "key": row[2],  # Still use 'key' in result dict for consistency
                "genre": genre  # Assume genre from query
            })

        conn.close()
        return results

    def _llm_select_best_track(self, compatible_tracks: List[Dict],
                                current_state: Dict) -> Dict:
        """Use LLM to select best track from compatible options."""

        # Build prompt for LLM
        prompt = f"""You are an expert DJ selecting the next track to play.

Current state:
- Playing: {(current_state.get('current_track') or {}).get('bpm', 128)} BPM, {(current_state.get('current_track') or {}).get('key', '8A')} key
- Energy level: {current_state.get('energy_level', 'medium')}
- Genre: {current_state.get('genre_preference', 'Techno')}
- Tracks played: {current_state.get('tracks_played', 0)}

Compatible tracks available:
{json.dumps(compatible_tracks[:5], indent=2)}

Select the best track considering:
1. Smooth BPM transition (prefer closer to current BPM)
2. Harmonic compatibility (Camelot Wheel)
3. Energy progression (gradually build or maintain)
4. Variety (don't repeat similar tracks)

Respond with JSON only:
{{
  "selected_track_index": 0,
  "reasoning": "brief explanation"
}}"""

        try:
            response = self.llm.chat([{"role": "user", "content": prompt}])
            decision = json.loads(response)

            selected_idx = decision.get("selected_track_index", 0)
            selected_track = compatible_tracks[selected_idx]

            # Extract folder name and track number from path
            track_path = selected_track["file_path"]
            folder_name = self._extract_folder_from_path(track_path)

            return {
                "folder_name": folder_name,
                "track_criteria": {
                    "bpm_min": selected_track["bpm"] - 2,
                    "bpm_max": selected_track["bpm"] + 2,
                    "compatible_keys": [selected_track["key"]],
                    "preferred_track_number": 1  # Will be refined during navigation
                },
                "reasoning": decision.get("reasoning", "LLM selection")
            }

        except Exception as e:
            # LLM failed, use fallback
            print(f"[WARN] LLM selection failed: {e}, using first compatible track")
            return self._fallback_track_decision(
                current_state.get('genre_preference', 'Techno'),
                current_state.get('energy_level', 'medium')
            )

    def _fallback_track_decision(self, genre: str, energy_level: str) -> Dict:
        """Fallback decision when no compatible tracks found."""
        energy_config = self.energy_levels.get(energy_level, self.energy_levels["medium"])
        bpm_range = energy_config["bpm_range"]

        return {
            "folder_name": genre,
            "track_criteria": {
                "bpm_min": bpm_range[0],
                "bpm_max": bpm_range[1],
                "compatible_keys": ["8A"],  # Default key
                "preferred_track_number": 1
            },
            "reasoning": "Fallback to default values (no compatible tracks found)"
        }

    def _extract_folder_from_path(self, path: str) -> str:
        """Extract folder name from track path."""
        # Example path: "Techno/Artist - Track.mp3"
        parts = path.split('/')
        if len(parts) > 1:
            return parts[0]
        return "Techno"  # Default

    def decide_mix_strategy(self, deck_a_state: Dict, deck_b_state: Dict) -> Dict:
        """
        Decide how to execute the mix between two decks.

        Returns: {
            "crossfader_duration_seconds": 8,
            "start_at_bars_remaining": 16,
            "eq_strategy": "gradual_bass_swap",
            "use_effects": false
        }
        """
        # Simple strategy for now (can be enhanced with LLM later)
        return {
            "crossfader_duration_seconds": 8,
            "start_at_bars_remaining": 16,
            "eq_strategy": "gradual_bass_swap",
            "use_effects": False,
            "reasoning": "Standard 8-second transition with bass EQ swap"
        }

    def should_load_next_track(self, playing_deck_state: Dict) -> bool:
        """
        Decide if it's time to load the next track.

        Args:
            playing_deck_state: {"bars_remaining": 24, "is_playing": True}

        Returns: True if should load next track
        """
        bars_remaining = playing_deck_state.get("bars_remaining", 100)
        is_playing = playing_deck_state.get("is_playing", False)

        # Trigger: less than 32 bars remaining and currently playing
        return is_playing and bars_remaining < 32
