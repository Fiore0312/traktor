"""
Autonomous DJ Orchestrator - Main Control Loop

Orchestrates autonomous DJ performance by coordinating:
- Brain (decision making)
- Navigator (track selection)
- MIDI Driver (Traktor control)
- Safety layer (validation)

State machine: IDLE → LOADING → PLAYING → MIXING → repeat
"""

import time
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from traktor_midi_driver import TraktorMIDIDriver
from autonomous_dj.autonomous_dj_brain import AutonomousDJBrain
from autonomous_dj.generated.autonomous_browser_navigator import AutonomousBrowserNavigator
from autonomous_dj.openrouter_client import OpenRouterClient
from traktor_safety_checks import TraktorSafetyChecks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DJState(Enum):
    """Autonomous DJ states"""
    IDLE = "idle"  # Nothing playing, ready to start
    LOADING = "loading"  # Loading next track
    PLAYING = "playing"  # One deck playing, waiting for transition
    MIXING = "mixing"  # Actively transitioning between decks
    PAUSED = "paused"  # User paused performance
    ERROR = "error"  # Error occurred


class AutonomousOrchestrator:
    """
    Main autonomous DJ orchestrator.

    Manages entire autonomous performance lifecycle:
    - Monitors playing deck timing
    - Decides when to load next track
    - Selects compatible tracks
    - Executes smooth transitions
    - Handles errors gracefully
    """

    def __init__(
        self,
        midi_driver: Optional[TraktorMIDIDriver] = None,
        brain: Optional[AutonomousDJBrain] = None,
        navigator: Optional[AutonomousBrowserNavigator] = None,
        safety_checker: Optional[TraktorSafetyChecks] = None,
        start_genre: str = "Techno",
        energy_level: str = "medium"
    ):
        """
        Initialize orchestrator.

        Args:
            midi_driver: MIDI driver instance (creates new if None)
            brain: DJ Brain instance (creates new if None)
            navigator: Browser navigator instance (creates new if None)
            safety_checker: Safety checker instance (creates new if None)
            start_genre: Initial genre to play
            energy_level: Initial energy level (low/medium/high/peak)
        """
        self.midi = midi_driver or TraktorMIDIDriver()
        self.brain = brain or AutonomousDJBrain()
        self.navigator = navigator or AutonomousBrowserNavigator(self.midi)
        self.safety = safety_checker or TraktorSafetyChecks(self.midi)

        # Genre mapping (Techno → House because Techno folder doesn't exist)
        genre_mapping = {
            "Techno": "House",
            "House": "House",
            "Dub": "Dub",
            "Deep House": "Deep House"
        }
        self.start_genre = genre_mapping.get(start_genre, start_genre)

        if start_genre != self.start_genre:
            print(f"ℹ️  Genre mapping: '{start_genre}' → '{self.start_genre}'")

        # Session state
        self.state = DJState.IDLE
        self.current_genre = start_genre
        self.energy_level = energy_level
        self.tracks_played = 0
        self.session_start_time = time.time()

        # Deck tracking
        self.playing_deck = None  # "A" or "B"
        self.loading_deck = None  # "A" or "B"
        self.deck_states = {
            "A": {"is_playing": False, "track": None, "bpm": None, "key": None},
            "B": {"is_playing": False, "track": None, "bpm": None, "key": None}
        }

        # Timing thresholds
        self.LOAD_TRIGGER_BARS = 32  # Load next track when <32 bars remaining
        self.MIX_START_BARS = 16  # Start mix transition at 16 bars remaining

        logger.info(f"[ORCHESTRATOR] Initialized - Genre: {start_genre}, Energy: {energy_level}")

    def start_session(self) -> bool:
        """
        Start autonomous DJ session.

        Returns: True if started successfully
        """
        logger.info("[ORCHESTRATOR] 🎧 STARTING AUTONOMOUS SESSION")

        if self.state != DJState.IDLE:
            logger.error(f"[ORCHESTRATOR] Cannot start - state is {self.state}")
            return False

        # Load first track on Deck A
        logger.info("[ORCHESTRATOR] Loading first track on Deck A...")
        success = self._load_first_track("A")

        if success:
            self.state = DJState.PLAYING
            self.playing_deck = "A"
            self.tracks_played = 1
            logger.info("[ORCHESTRATOR] ✅ Session started successfully")
            return True
        else:
            self.state = DJState.ERROR
            logger.error("[ORCHESTRATOR] ❌ Failed to load first track")
            return False

    def _load_first_track(self, deck: str) -> bool:
        """
        Load first track of session.

        Args:
            deck: "A" or "B"

        Returns: True if loaded successfully
        """
        # Get initial track decision from Brain
        initial_state = {
            "playing_deck": None,
            "current_track": None,
            "energy_level": self.energy_level,
            "genre_preference": self.current_genre,
            "tracks_played": 0,
            "session_duration_minutes": 0
        }

        decision = self.brain.decide_next_track(initial_state)
        folder = decision["folder_name"]
        track_number = decision["track_criteria"]["preferred_track_number"]

        logger.info(f"[ORCHESTRATOR] Brain selected: {folder}, track {track_number}")

        # Navigate to track
        success, msg = self.navigator.navigate_and_select_track(folder, track_number)
        if not success:
            logger.error(f"[ORCHESTRATOR] Navigation failed: {msg}")
            return False

        # Load to deck
        time.sleep(0.5)  # Wait for navigation to settle
        load_success = self.midi.load_selected_track(deck)
        if not load_success:
            logger.error(f"[ORCHESTRATOR] Failed to load track to deck {deck}")
            return False

        # Configure deck for playback
        time.sleep(1.0)  # Wait for track to load

        # Set as MASTER (first track, nothing to sync to)
        self.midi.set_master_mode(deck, True)

        # Set volume to 85%
        self.midi.set_volume(deck, 108)  # 85% of 127 ≈ 108

        # Crossfader to deck position
        if deck == "A":
            self.midi.set_crossfader(0)  # Full left
        else:
            self.midi.set_crossfader(127)  # Full right

        # Update deck state
        self.deck_states[deck] = {
            "is_playing": False,  # Not playing yet
            "track": f"{folder}/track_{track_number}",
            "bpm": decision["track_criteria"]["bpm_min"],  # Approximate
            "key": decision["track_criteria"]["compatible_keys"][0]  # First compatible key
        }

        # Start playback
        time.sleep(0.5)
        play_success = self.midi.play_deck(deck)

        if play_success:
            self.deck_states[deck]["is_playing"] = True
            logger.info(f"[ORCHESTRATOR] ✅ Deck {deck} playing")
            return True
        else:
            logger.error(f"[ORCHESTRATOR] Failed to start playback on deck {deck}")
            return False

    def main_loop(self, max_tracks: Optional[int] = None, check_interval: float = 2.0):
        """
        Main autonomous loop.

        Args:
            max_tracks: Maximum tracks to play (None = infinite)
            check_interval: Seconds between state checks
        """
        logger.info(f"[ORCHESTRATOR] 🔄 MAIN LOOP STARTED (max_tracks={max_tracks})")

        try:
            while True:
                # Check stop condition
                if max_tracks and self.tracks_played >= max_tracks:
                    logger.info(f"[ORCHESTRATOR] ✅ Reached max tracks ({max_tracks})")
                    break

                # State machine
                if self.state == DJState.PLAYING:
                    self._handle_playing_state()
                elif self.state == DJState.LOADING:
                    self._handle_loading_state()
                elif self.state == DJState.MIXING:
                    self._handle_mixing_state()
                elif self.state == DJState.ERROR:
                    logger.error("[ORCHESTRATOR] Error state - stopping")
                    break
                elif self.state == DJState.PAUSED:
                    logger.info("[ORCHESTRATOR] Paused - waiting...")

                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("[ORCHESTRATOR] ⏹️  Stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] ❌ Error in main loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()

    def _handle_playing_state(self):
        """Handle PLAYING state - monitor timing, decide when to load next track."""

        # Simulate bars remaining (in real implementation, would read from Traktor UI)
        # For now, use time-based estimation
        bars_remaining = self._estimate_bars_remaining(self.playing_deck)

        logger.info(f"[ORCHESTRATOR] Playing {self.playing_deck}, ~{bars_remaining} bars remaining")

        # Check if should load next track
        deck_state = {
            "bars_remaining": bars_remaining,
            "is_playing": self.deck_states[self.playing_deck]["is_playing"]
        }

        should_load = self.brain.should_load_next_track(deck_state)

        if should_load and self.loading_deck is None:
            logger.info("[ORCHESTRATOR] 🔄 Time to load next track")
            self.state = DJState.LOADING

    def _handle_loading_state(self):
        """Handle LOADING state - load next track on idle deck."""

        # Determine target deck (opposite of playing)
        target_deck = "B" if self.playing_deck == "A" else "A"
        self.loading_deck = target_deck

        logger.info(f"[ORCHESTRATOR] 📀 Loading next track on Deck {target_deck}")

        # Get current state for Brain
        current_track = self.deck_states[self.playing_deck]
        current_state = {
            "playing_deck": self.playing_deck,
            "current_track": {
                "bpm": current_track.get("bpm", 128),
                "key": current_track.get("key", "8A"),
                "genre": self.current_genre
            },
            "energy_level": self.energy_level,
            "genre_preference": self.current_genre,
            "tracks_played": self.tracks_played,
            "session_duration_minutes": (time.time() - self.session_start_time) / 60
        }

        # Brain decides next track
        decision = self.brain.decide_next_track(current_state)
        folder = decision["folder_name"]
        track_number = decision["track_criteria"]["preferred_track_number"]

        logger.info(f"[ORCHESTRATOR] Brain selected: {folder}, track {track_number}")
        logger.info(f"[ORCHESTRATOR] Reasoning: {decision['reasoning']}")

        # Navigate and load
        success, msg = self.navigator.navigate_and_select_track(folder, track_number)
        if not success:
            logger.error(f"[ORCHESTRATOR] Navigation failed: {msg}")
            self.state = DJState.ERROR
            return

        time.sleep(0.5)
        load_success = self.midi.load_selected_track(target_deck)
        if not load_success:
            logger.error(f"[ORCHESTRATOR] Failed to load track")
            self.state = DJState.ERROR
            return

        # Configure new deck for mixing
        time.sleep(1.0)  # Wait for track to load

        # Enable SYNC (will sync to playing deck)
        self.midi.enable_sync(target_deck, True)

        # Set volume to 0 (will fade in during mix)
        self.midi.set_volume(target_deck, 0)

        # Update deck state
        self.deck_states[target_deck] = {
            "is_playing": False,
            "track": f"{folder}/track_{track_number}",
            "bpm": decision["track_criteria"]["bpm_min"],
            "key": decision["track_criteria"]["compatible_keys"][0]
        }

        logger.info(f"[ORCHESTRATOR] ✅ Track loaded on Deck {target_deck}, ready to mix")

        # Transition to MIXING state
        self.state = DJState.MIXING

    def _handle_mixing_state(self):
        """Handle MIXING state - execute crossfader transition."""

        logger.info("[ORCHESTRATOR] 🎚️  Starting mix transition")

        source_deck = self.playing_deck
        target_deck = self.loading_deck

        # Get mix strategy from Brain
        deck_a_state = self.deck_states["A"]
        deck_b_state = self.deck_states["B"]
        strategy = self.brain.decide_mix_strategy(deck_a_state, deck_b_state)

        duration = strategy["crossfader_duration_seconds"]
        logger.info(f"[ORCHESTRATOR] Mix duration: {duration}s")

        # Wait for optimal mix point
        bars_remaining = self._estimate_bars_remaining(source_deck)
        target_bars = strategy["start_at_bars_remaining"]

        if bars_remaining > target_bars:
            wait_time = (bars_remaining - target_bars) * 2  # ~2 seconds per bar at 128 BPM
            logger.info(f"[ORCHESTRATOR] Waiting {wait_time:.1f}s for mix point ({target_bars} bars)")
            time.sleep(wait_time)

        # Start target deck
        logger.info(f"[ORCHESTRATOR] ▶️  Starting Deck {target_deck}")
        self.midi.play_deck(target_deck)
        self.deck_states[target_deck]["is_playing"] = True

        # Execute crossfader transition
        steps = 20  # Number of crossfader steps
        step_duration = duration / steps

        start_pos = 0 if source_deck == "A" else 127
        end_pos = 127 if source_deck == "A" else 0

        logger.info(f"[ORCHESTRATOR] Crossfading from {source_deck} to {target_deck}")

        for i in range(steps + 1):
            progress = i / steps
            current_pos = int(start_pos + (end_pos - start_pos) * progress)
            self.midi.set_crossfader(current_pos)
            time.sleep(step_duration)

        logger.info("[ORCHESTRATOR] ✅ Mix complete")

        # Stop and reset source deck
        time.sleep(1.0)
        self.midi.pause_deck(source_deck)
        self.deck_states[source_deck]["is_playing"] = False
        self.midi.set_volume(source_deck, 0)

        # Update playing deck
        self.playing_deck = target_deck
        self.loading_deck = None
        self.tracks_played += 1

        logger.info(f"[ORCHESTRATOR] Now playing: Deck {self.playing_deck}")
        logger.info(f"[ORCHESTRATOR] Tracks played: {self.tracks_played}")

        # Return to PLAYING state
        self.state = DJState.PLAYING

    def _estimate_bars_remaining(self, deck: str) -> int:
        """
        Estimate bars remaining (placeholder - would read from Traktor UI in production).

        In production, this would:
        - Read from Traktor UI via vision system
        - Or use MIDI feedback if available
        - Or track playback time manually

        For now, returns simulated value based on time.
        """
        # Simulate: assume 4-minute tracks, 128 BPM = 512 bars total
        # Gradually decrease over time
        track_load_time = getattr(self, f"_deck_{deck}_load_time", time.time())
        elapsed = time.time() - track_load_time
        total_duration = 240  # 4 minutes
        total_bars = 512

        bars_elapsed = int((elapsed / total_duration) * total_bars)
        bars_remaining = max(0, total_bars - bars_elapsed)

        return bars_remaining

    def _cleanup(self):
        """Cleanup resources on shutdown."""
        logger.info("[ORCHESTRATOR] 🧹 Cleaning up...")

        # Stop all decks
        for deck in ["A", "B"]:
            if self.deck_states[deck]["is_playing"]:
                self.midi.pause_deck(deck)

        # Reset crossfader to center
        self.midi.set_crossfader(64)

        # Reset volumes
        for deck in ["A", "B"]:
            self.midi.set_volume(deck, 85)

        logger.info("[ORCHESTRATOR] ✅ Cleanup complete")

    def stop_session(self):
        """Stop autonomous session gracefully."""
        logger.info("[ORCHESTRATOR] ⏹️  Stopping session")
        self.state = DJState.PAUSED
        self._cleanup()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎧 AUTONOMOUS DJ ORCHESTRATOR - TEST MODE")
    print("=" * 70)
    print("\n⚠️  This is a simulation mode for testing.")
    print("In production, this would be started by workflow_controller.py\n")

    orchestrator = AutonomousOrchestrator(
        start_genre="Techno",
        energy_level="medium"
    )

    print("Starting session...")
    success = orchestrator.start_session()

    if success:
        print("\n✅ Session started successfully!")
        print("\nRunning main loop (max 3 tracks for testing)...")
        orchestrator.main_loop(max_tracks=3, check_interval=1.0)
    else:
        print("\n❌ Failed to start session")
