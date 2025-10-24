"""
State Manager - Coordinated shared state between processes
Uses JSON files + file locking for atomic operations
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, fields
from filelock import FileLock
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config.config_loader import get_config


@dataclass
class PerformanceState:
    """Current performance state"""

    is_playing: bool = False
    current_track_position: int = 0
    current_genre: str = "house"
    setlist_loaded: bool = False
    setlist_id: str = ""

    # Deck states
    deck_a_playing: bool = False
    deck_b_playing: bool = False
    deck_a_track: Optional[str] = None
    deck_b_track: Optional[str] = None

    # Timing
    performance_start_time: Optional[float] = None
    current_track_start_time: Optional[float] = None
    next_transition_bar: Optional[int] = None

    # Background operations
    background_preparing_genre: Optional[str] = None
    background_ready: bool = False
    background_progress: str = ""

    # Stats
    tracks_played: int = 0
    transitions_executed: int = 0
    total_performance_time_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceState":
        """Create from dict, filtering unknown keys"""
        known_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered_data)


class StateManager:
    """
    Manages shared state between live_performer and background_intelligence

    Thread-safe via file locking
    """

    def __init__(self, state_file: Path = None):
        if state_file is None:
            # Default to data/state.json in project root
            project_root = Path(__file__).parent.parent
            state_file = project_root / "data" / "state.json"

        self.state_file = state_file
        self.lock_file = state_file.with_suffix(".lock")
        self._cache = None
        self._cache_time = 0
        self._cache_ttl = 0.1  # Cache for 100ms to reduce file I/O

    def _read_state(self) -> Dict[str, Any]:
        """Read state from file (with locking)"""
        lock = FileLock(self.lock_file)

        with lock:
            if not self.state_file.exists():
                # Initialize with default state
                default_state = PerformanceState()
                self.state_file.write_text(json.dumps(default_state.to_dict(), indent=2))
                return default_state.to_dict()

            return json.loads(self.state_file.read_text())

    def _write_state(self, state: Dict[str, Any]):
        """Write state to file (with locking)"""
        lock = FileLock(self.lock_file)

        with lock:
            self.state_file.write_text(json.dumps(state, indent=2))

        # Invalidate cache
        self._cache = None

    def get_state(self, use_cache: bool = True) -> PerformanceState:
        """
        Get current state

        Args:
            use_cache: Use cached state if recent (reduces file I/O)
        """
        now = time.time()

        if use_cache and self._cache and (now - self._cache_time) < self._cache_ttl:
            return PerformanceState.from_dict(self._cache)

        data = self._read_state()
        self._cache = data
        self._cache_time = now

        return PerformanceState.from_dict(data)

    def update_state(self, **kwargs):
        """
        Update state fields

        Example:
            state_manager.update_state(
                is_playing=True,
                current_track_position=2
            )
        """
        current = self._read_state()
        current.update(kwargs)
        self._write_state(current)

    def reset(self):
        """Reset to default state"""
        default_state = PerformanceState()
        self._write_state(default_state.to_dict())

    def start_performance(self, genre: str, setlist_id: str):
        """Mark performance as started"""
        self.update_state(
            is_playing=True,
            current_genre=genre,
            setlist_id=setlist_id,
            setlist_loaded=True,
            performance_start_time=time.time(),
            tracks_played=0,
            transitions_executed=0,
        )

    def stop_performance(self):
        """Mark performance as stopped"""
        state = self.get_state()
        elapsed = time.time() - (state.performance_start_time or time.time())

        self.update_state(is_playing=False, total_performance_time_sec=elapsed)

    def start_background_preparation(self, genre: str):
        """Mark background as preparing new genre"""
        self.update_state(
            background_preparing_genre=genre, background_ready=False, background_progress="Starting..."
        )

    def update_background_progress(self, progress: str):
        """Update background progress message"""
        self.update_state(background_progress=progress)

    def mark_background_ready(self):
        """Mark background preparation complete"""
        self.update_state(background_ready=True, background_progress="Ready for switch!")

    def clear_background(self):
        """Clear background preparation state"""
        self.update_state(
            background_preparing_genre=None, background_ready=False, background_progress=""
        )


# Global state manager instance
state_manager = StateManager()
