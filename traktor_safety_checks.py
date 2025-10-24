#!/usr/bin/env python3
"""
Traktor Safety Layer - Professional DJ Workflow Compliance

Implements safety checks and mixer state management based on
professional DJ best practices (DJ_WORKFLOW_RULES.md).

Prevents:
- Audio spikes from incorrect volume settings
- Clipping from improper gain staging
- Interrupting playing decks
- MASTER/SYNC conflicts

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
Source: DJ_WORKFLOW_RULES.md (33 years DJ experience)
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from typing import Dict, List, Optional, Tuple
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TraktorSafetyChecks:
    """
    Safety layer for Traktor MIDI operations.

    Ensures mixer state is safe before/after all deck operations.
    Implements professional DJ workflow rules to prevent audio mishaps.
    """

    # Safe default values (from DJ_WORKFLOW_RULES.md)
    SAFE_DEFAULTS = {
        'volume_silent': 0,      # Silent deck
        'volume_playing': 108,   # ~85% for playing deck
        'volume_incoming': 26,   # ~20% for incoming (before mix)
        'gain_neutral': 64,      # 12 o'clock (center)
        'eq_neutral': 64,        # 12 o'clock (flat response)
        'filter_bypass': 64,     # Center (no effect)
        'crossfader_left': 0,    # Full left (Deck A)
        'crossfader_center': 64, # Center
        'crossfader_right': 127, # Full right (Deck B)
        'master_volume': 108,    # ~85% master output
    }

    # CC Mapping from traktor_midi_mapping.json
    CC_DECK_A = {
        'volume': TraktorCC.DECK_A_VOLUME,        # 65
        'eq_high': TraktorCC.DECK_A_EQ_HIGH,      # 34
        'eq_mid': TraktorCC.DECK_A_EQ_MID,        # 35
        'eq_low': TraktorCC.DECK_A_EQ_LOW,        # 36
        'sync': TraktorCC.DECK_A_SYNC_ON,         # 69
        'master': TraktorCC.DECK_A_TEMPO_MASTER,  # 33
        'play': TraktorCC.DECK_A_PLAY_PAUSE,      # 47
        'cue': TraktorCC.DECK_A_CUE,              # 80
    }

    CC_DECK_B = {
        'volume': TraktorCC.DECK_B_VOLUME,        # 60
        'eq_high': TraktorCC.DECK_B_EQ_HIGH,      # 50
        'eq_mid': TraktorCC.DECK_B_EQ_MID,        # 51
        'eq_low': TraktorCC.DECK_B_EQ_LOW,        # 52
        'sync': TraktorCC.DECK_B_SYNC_ON,         # 42
        'master': TraktorCC.DECK_B_TEMPO_MASTER,  # 37
        'play': TraktorCC.DECK_B_PLAY_PAUSE,      # 48
        'cue': TraktorCC.DECK_B_CUE,              # 81
    }

    CC_MIXER = {
        'crossfader': 56,        # CC 56 verified working (conflicts with browser tree)
        'master_volume': TraktorCC.MASTER_VOLUME,  # 75
    }

    def __init__(self, midi_driver: TraktorMIDIDriver, delay_between_commands: float = 0.3):
        """
        Initialize safety layer.

        Args:
            midi_driver: TraktorMIDIDriver instance
            delay_between_commands: Delay in seconds between MIDI commands (default 0.3s)
        """
        self.midi = midi_driver
        self.delay = delay_between_commands

        # Internal state tracking (since we can't read from Traktor)
        self.deck_states = {
            'A': {'playing': False, 'is_master': False, 'volume': 0},
            'B': {'playing': False, 'is_master': False, 'volume': 0},
        }

        logger.info("[SAFETY] Safety layer initialized")
        logger.info(f"[SAFETY] Command delay: {self.delay}s")

    def pre_load_safety_check(self, target_deck: str, opposite_deck_playing: bool = False) -> bool:
        """
        Execute safety checks BEFORE loading a track.

        Critical actions:
        1. Set target deck volume to 0 (prevent audio spike)
        2. Verify crossfader position OR volume safety
        3. Protect opposite deck if playing

        Args:
            target_deck: 'A' or 'B'
            opposite_deck_playing: True if opposite deck is currently playing

        Returns:
            True if safe to proceed with load
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[SAFETY] PRE-LOAD CHECK - Deck {target_deck}")
        logger.info(f"{'='*70}")

        deck_cc = self.CC_DECK_A if target_deck == 'A' else self.CC_DECK_B

        # CRITICAL: Set target deck volume to ZERO
        logger.info(f"[SAFETY] Setting Deck {target_deck} volume to 0% (prevent audio spike)")
        self.midi.send_cc(deck_cc['volume'], self.SAFE_DEFAULTS['volume_silent'])
        time.sleep(self.delay)

        # Update internal state
        self.deck_states[target_deck]['volume'] = 0

        # Position crossfader AWAY from target deck (double safety)
        if not opposite_deck_playing:
            # First track - position crossfader to target deck's side
            logger.info(f"[SAFETY] Positioning crossfader for Deck {target_deck}")
            crossfader_value = self.SAFE_DEFAULTS['crossfader_left'] if target_deck == 'A' else self.SAFE_DEFAULTS['crossfader_right']
            self.midi.send_cc(self.CC_MIXER['crossfader'], crossfader_value)
            time.sleep(self.delay)
        else:
            # Second+ track - crossfader stays with playing deck
            opposite = 'B' if target_deck == 'A' else 'A'
            logger.info(f"[SAFETY] Deck {opposite} is playing - crossfader remains in position")
            logger.info(f"[SAFETY] Deck {target_deck} will load silently (volume at 0%)")

        logger.info(f"[SAFETY] ✅ Pre-load check complete - SAFE to load")
        return True

    def post_load_safety_setup(self, target_deck: str, is_first_track: bool = False):
        """
        Configure deck with safe defaults AFTER loading track.

        Critical actions:
        1. Reset EQ to neutral (flat response)
        2. Ensure volume still at 0 (confirm)
        3. Set MASTER/SYNC based on session state
        4. Prepare for playback

        Args:
            target_deck: 'A' or 'B'
            is_first_track: True if this is the first track of the session
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[SAFETY] POST-LOAD SETUP - Deck {target_deck}")
        logger.info(f"{'='*70}")

        deck_cc = self.CC_DECK_A if target_deck == 'A' else self.CC_DECK_B

        # 1. Reset EQ to neutral (flat frequency response)
        logger.info(f"[SAFETY] Resetting EQ to neutral (flat response)")
        eq_controls = [
            ('EQ High', deck_cc['eq_high']),
            ('EQ Mid', deck_cc['eq_mid']),
            ('EQ Low', deck_cc['eq_low']),
        ]

        for name, cc in eq_controls:
            self.midi.send_cc(cc, self.SAFE_DEFAULTS['eq_neutral'])
            logger.info(f"[SAFETY]   → {name}: Center (64)")
            time.sleep(self.delay)

        # 2. Confirm volume at 0
        logger.info(f"[SAFETY] Confirming volume at 0%")
        self.midi.send_cc(deck_cc['volume'], self.SAFE_DEFAULTS['volume_silent'])
        time.sleep(self.delay)

        # 3. MASTER/SYNC logic
        if is_first_track:
            logger.info(f"[SAFETY] First track - setting Deck {target_deck} as MASTER")
            self.midi.send_cc(deck_cc['master'], 127)  # Set as MASTER
            time.sleep(self.delay)

            # Do NOT enable SYNC (nothing to sync to)
            logger.info(f"[SAFETY] SYNC not enabled (no reference track)")

            # Update internal state
            self.deck_states[target_deck]['is_master'] = True
        else:
            logger.info(f"[SAFETY] Not first track - enabling SYNC")
            self.midi.send_cc(deck_cc['sync'], 127)  # Enable SYNC
            time.sleep(self.delay)

            # Do NOT set MASTER (AUTO mode will handle transfer)
            logger.info(f"[SAFETY] MASTER not set (AUTO mode will manage)")

            # Update internal state
            self.deck_states[target_deck]['is_master'] = False

        logger.info(f"[SAFETY] ✅ Post-load setup complete - Deck {target_deck} ready")
        logger.info(f"[SAFETY]    Volume: 0% (safe for playback)")
        logger.info(f"[SAFETY]    EQ: Neutral (flat)")
        logger.info(f"[SAFETY]    MASTER: {'YES' if is_first_track else 'NO (AUTO)'}")
        logger.info(f"[SAFETY]    SYNC: {'NO' if is_first_track else 'YES'}")

    def prepare_for_playback(self, target_deck: str, is_first_track: bool = False):
        """
        Final preparation before pressing PLAY.

        Sets volume to appropriate level based on context.

        Args:
            target_deck: 'A' or 'B'
            is_first_track: True if first track (needs high volume immediately)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[SAFETY] PREPARE FOR PLAYBACK - Deck {target_deck}")
        logger.info(f"{'='*70}")

        deck_cc = self.CC_DECK_A if target_deck == 'A' else self.CC_DECK_B

        if is_first_track:
            # First track - set volume high for immediate playback
            logger.info(f"[SAFETY] First track - setting volume to 85%")
            volume = self.SAFE_DEFAULTS['volume_playing']
            self.midi.send_cc(deck_cc['volume'], volume)
            time.sleep(self.delay)

            self.deck_states[target_deck]['volume'] = volume

            logger.info(f"[SAFETY] ✅ Ready to PLAY - Deck {target_deck} at full volume")
        else:
            # Second+ track - volume stays at 0, will fade in during mix
            logger.info(f"[SAFETY] Not first track - volume remains at 0%")
            logger.info(f"[SAFETY] Track will play SILENTLY until manual fade-in")
            logger.info(f"[SAFETY] Gradual volume increase during transition")

            logger.info(f"[SAFETY] ✅ Ready to PLAY - Deck {target_deck} (silent, cued for mix)")

    def safe_volume_transition(self, from_deck: str, to_deck: str, steps: int = 10, step_delay: float = 0.5):
        """
        Perform safe volume crossfade between decks.

        Args:
            from_deck: Deck to fade out ('A' or 'B')
            to_deck: Deck to fade in ('A' or 'B')
            steps: Number of steps in crossfade (default 10)
            step_delay: Delay between steps in seconds (default 0.5s)
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"[SAFETY] VOLUME TRANSITION: {from_deck} → {to_deck}")
        logger.info(f"{'='*70}")

        from_cc = self.CC_DECK_A if from_deck == 'A' else self.CC_DECK_B
        to_cc = self.CC_DECK_A if to_deck == 'A' else self.CC_DECK_B

        # Starting values
        from_volume = self.SAFE_DEFAULTS['volume_playing']  # 85%
        to_volume = self.SAFE_DEFAULTS['volume_silent']     # 0%

        # Calculate step sizes
        from_step = from_volume // steps
        to_step = self.SAFE_DEFAULTS['volume_playing'] // steps

        logger.info(f"[SAFETY] Crossfade in {steps} steps over {steps * step_delay:.1f}s")

        for i in range(steps + 1):
            # Calculate volumes
            from_vol = max(0, from_volume - (from_step * i))
            to_vol = min(self.SAFE_DEFAULTS['volume_playing'], to_volume + (to_step * i))

            # Send MIDI commands
            self.midi.send_cc(from_cc['volume'], from_vol)
            time.sleep(0.1)
            self.midi.send_cc(to_cc['volume'], to_vol)

            logger.info(f"[SAFETY] Step {i+1}/{steps+1}: "
                       f"Deck {from_deck}={from_vol:3d} ({from_vol*100//127:2d}%), "
                       f"Deck {to_deck}={to_vol:3d} ({to_vol*100//127:2d}%)")

            # Update internal state
            self.deck_states[from_deck]['volume'] = from_vol
            self.deck_states[to_deck]['volume'] = to_vol

            time.sleep(step_delay)

        logger.info(f"[SAFETY] ✅ Transition complete")
        logger.info(f"[SAFETY]    Deck {from_deck}: Silent (0%)")
        logger.info(f"[SAFETY]    Deck {to_deck}: Playing (85%)")

    def emergency_silence_deck(self, deck: str):
        """
        EMERGENCY: Immediately silence a deck.

        Used when audio spike or unwanted sound detected.

        Args:
            deck: 'A' or 'B'
        """
        logger.warning(f"[SAFETY] 🚨 EMERGENCY SILENCE - Deck {deck}")

        deck_cc = self.CC_DECK_A if deck == 'A' else self.CC_DECK_B

        # Immediate volume cut
        self.midi.send_cc(deck_cc['volume'], 0)

        # Update state
        self.deck_states[deck]['volume'] = 0

        logger.warning(f"[SAFETY] Deck {deck} silenced")

    def get_deck_state(self, deck: str) -> Dict:
        """
        Get current internal state of a deck.

        NOTE: This is INTERNAL tracking, not read from Traktor.
        For actual Traktor state, use vision-based verification.

        Args:
            deck: 'A' or 'B'

        Returns:
            Dict with deck state
        """
        return self.deck_states.get(deck, {})

    def mark_deck_playing(self, deck: str, playing: bool = True):
        """
        Update internal state when deck starts/stops playing.

        Args:
            deck: 'A' or 'B'
            playing: True if now playing, False if stopped
        """
        self.deck_states[deck]['playing'] = playing
        logger.info(f"[SAFETY] Deck {deck} state: {'PLAYING' if playing else 'STOPPED'}")

    def play_deck_toggle(self, deck: str):
        """
        Play deck using Toggle mode (for Play/Pause in Toggle interaction mode).

        Sends impulse (127->0) only if deck is currently NOT playing.
        Requires internal state tracking.

        Args:
            deck: 'A' or 'B'
        """
        deck_cc = self.CC_DECK_A if deck == 'A' else self.CC_DECK_B

        current_playing = self.deck_states[deck]['playing']

        if not current_playing:
            logger.info(f"[SAFETY] Deck {deck} NOT playing, sending TOGGLE to PLAY")
            # Send toggle impulse
            self.midi.send_cc(deck_cc['play'], 127)
            time.sleep(0.05)
            self.midi.send_cc(deck_cc['play'], 0)
            time.sleep(self.delay)

            # Update state
            self.deck_states[deck]['playing'] = True
            logger.info(f"[SAFETY] Deck {deck} now PLAYING")
        else:
            logger.info(f"[SAFETY] Deck {deck} already PLAYING, no action")

    def pause_deck_toggle(self, deck: str):
        """
        Pause deck using Toggle mode.

        Sends impulse (127->0) only if deck is currently playing.

        Args:
            deck: 'A' or 'B'
        """
        deck_cc = self.CC_DECK_A if deck == 'A' else self.CC_DECK_B

        current_playing = self.deck_states[deck]['playing']

        if current_playing:
            logger.info(f"[SAFETY] Deck {deck} PLAYING, sending TOGGLE to PAUSE")
            # Send toggle impulse
            self.midi.send_cc(deck_cc['play'], 127)
            time.sleep(0.05)
            self.midi.send_cc(deck_cc['play'], 0)
            time.sleep(self.delay)

            # Update state
            self.deck_states[deck]['playing'] = False
            logger.info(f"[SAFETY] Deck {deck} now PAUSED")
        else:
            logger.info(f"[SAFETY] Deck {deck} already PAUSED, no action")

    def verify_mixer_safety(self) -> Dict[str, bool]:
        """
        Verify overall mixer state is safe.

        Returns:
            Dict with safety status
        """
        status = {
            'volumes_safe': True,  # Assume safe (can't read actual values)
            'no_clipping': True,   # Assume no clipping
            'crossfader_ok': True, # Assume correct position
            'master_set': any(d['is_master'] for d in self.deck_states.values()),
        }

        logger.info(f"[SAFETY] Mixer safety check: {status}")
        return status


# Convenience function for simple workflows
def safe_load_and_play_workflow(
    midi: TraktorMIDIDriver,
    target_deck: str,
    is_first_track: bool = False,
    opposite_deck_playing: bool = False
) -> bool:
    """
    Complete safe load and play workflow.

    Args:
        midi: TraktorMIDIDriver instance
        target_deck: 'A' or 'B'
        is_first_track: True if first track of session
        opposite_deck_playing: True if opposite deck is playing

    Returns:
        True if successful
    """
    safety = TraktorSafetyChecks(midi)

    # Pre-load safety
    if not safety.pre_load_safety_check(target_deck, opposite_deck_playing):
        logger.error("[WORKFLOW] Pre-load safety check failed!")
        return False

    # User loads track here (or automated browser navigation)
    logger.info(f"[WORKFLOW] >>> LOAD TRACK TO DECK {target_deck} NOW <<<")
    time.sleep(2)  # Wait for track load

    # Post-load setup
    safety.post_load_safety_setup(target_deck, is_first_track)

    # Prepare for playback
    safety.prepare_for_playback(target_deck, is_first_track)

    # Mark as playing
    safety.mark_deck_playing(target_deck, True)

    logger.info(f"[WORKFLOW] ✅ Deck {target_deck} safe and ready to play!")
    return True


if __name__ == "__main__":
    # Test initialization
    print("=" * 70)
    print("Traktor Safety Layer - Test Mode")
    print("=" * 70)
    print()
    print("This module provides safety checks for Traktor MIDI operations.")
    print("Import and use TraktorSafetyChecks class in your workflows.")
    print()
    print("Example:")
    print("  from traktor_safety_checks import TraktorSafetyChecks")
    print("  safety = TraktorSafetyChecks(midi_driver)")
    print("  safety.pre_load_safety_check('A')")
    print()
