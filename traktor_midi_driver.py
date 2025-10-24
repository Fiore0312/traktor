#!/usr/bin/env python3
"""
TRAKTOR PRO 3 MIDI DRIVER
=========================
Python MIDI driver for Traktor Pro 3 integration (Cross-platform: Windows/macOS)

Features:
- Low-latency MIDI communication (<10ms target)
- Automatic MIDI port detection (Windows: loopMIDI, macOS: IAC Driver)
- Type-safe MIDI message construction
- Comprehensive error handling
- Connection state management
- Cross-platform compatibility

Author: DJ Fiore AI System
Version: 2.0
Created: 2025-10-08
Updated: 2025-10-10 (Windows compatibility)
"""

import time
import logging
import platform
import pygame  # For pygame.midi backend on Windows
from typing import Optional, List, Tuple
from enum import IntEnum

# Cross-platform MIDI support: mido (Windows) or rtmidi (macOS)
_USING_MIDO = False
try:
    if platform.system() == "Windows":
        # Windows: use mido with pygame backend (no compiler needed)
        import os
        os.environ['MIDO_BACKEND'] = 'mido.backends.pygame'
        import mido
        # Set pygame backend explicitly
        try:
            mido.set_backend('mido.backends.pygame')
        except:
            pass  # Backend might already be set
        _USING_MIDO = True
        CONTROL_CHANGE = 0xB0
    else:
        # macOS: use rtmidi
        import rtmidi
        from rtmidi.midiconstants import CONTROL_CHANGE
except ImportError as e:
    if platform.system() == "Windows":
        raise ImportError(
            "mido and pygame not found. Install with: pip install mido pygame"
        ) from e
    else:
        raise ImportError(
            "python-rtmidi not found. Install with: pip install python-rtmidi"
        ) from e


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MIDIChannel(IntEnum):
    """MIDI Channels for Traktor communication"""
    AI_CONTROL = 0      # Channel 1 - AI Agent Control (Input to Traktor)
    STATUS_FEEDBACK = 1  # Channel 2 - Status Feedback (Output from Traktor)
    HUMAN_OVERRIDE = 2   # Channel 3 - Human Override Controls
    EFFECTS = 3          # Channel 4 - Effects Control


class TraktorCC(IntEnum):
    """Traktor Pro 3 MIDI CC assignments - DEFINITIVE from Screenshots 2025-10-08"""

    # =========== TRANSPORT CONTROLS (VERIFIED!) ===========
    DECK_A_PLAY_PAUSE = 47
    DECK_B_PLAY_PAUSE = 48
    DECK_C_PLAY_PAUSE = 90
    DECK_D_PLAY_PAUSE = 91

    # =========== TRACK LOADING (VERIFIED!) ===========
    DECK_A_LOAD_TRACK = 43
    DECK_B_LOAD_TRACK = 44
    DECK_C_LOAD_TRACK = 45
    DECK_D_LOAD_TRACK = 46

    # =========== CUE CONTROLS (VERIFIED!) ===========
    DECK_A_CUE = 80
    DECK_B_CUE = 81
    DECK_C_CUE = 82
    DECK_D_CUE = 83

    # =========== TEMPO MASTER (VERIFIED!) ===========
    DECK_A_TEMPO_MASTER = 33
    DECK_B_TEMPO_MASTER = 37
    DECK_C_TEMPO_MASTER = 38
    DECK_D_TEMPO_MASTER = 39

    # =========== SYNC/GRID (VERIFIED!) ===========
    DECK_A_SYNC_GRID = 24
    DECK_B_SYNC_GRID = 25
    DECK_B_SYNC_ON = 42
    DECK_C_SYNC_ON = 59
    DECK_D_SYNC_ON = 63
    DECK_A_SYNC_ON = 69
    DECK_C_SYNC_ON_ALT = 70
    DECK_D_SYNC_ON_ALT = 71

    # =========== VOLUME CONTROLS (VERIFIED!) ===========
    MASTER_VOLUME = 75
    DECK_A_VOLUME = 65
    DECK_B_VOLUME = 60
    DECK_C_VOLUME = 61
    DECK_D_VOLUME = 62

    # =========== EQ CONTROLS (VERIFIED!) ===========
    DECK_A_EQ_HIGH = 34
    DECK_A_EQ_MID = 35
    DECK_A_EQ_LOW = 36
    DECK_B_EQ_HIGH = 50
    DECK_B_EQ_MID = 51
    DECK_B_EQ_LOW = 52
    DECK_C_EQ_HIGH = 84
    DECK_C_EQ_MID = 85
    DECK_C_EQ_LOW = 86
    DECK_D_EQ_HIGH = 66
    DECK_D_EQ_MID = 67
    DECK_D_EQ_LOW = 68

    # =========== TEMPO/PITCH (VERIFIED!) ===========
    DECK_A_TEMPO = 41
    DECK_B_TEMPO = 40
    DECK_C_TEMPO = 2
    DECK_D_TEMPO = 3

    # =========== BROWSER NAVIGATION (VERIFIED!) ===========
    BROWSER_SCROLL_LIST = 74
    BROWSER_SCROLL_TREE_DEC = 73
    BROWSER_SCROLL_TREE_INC = 72
    BROWSER_EXPAND_COLLAPSE = 64

    # =========== LOOP CONTROLS (VERIFIED!) ===========
    DECK_A_LOOP_ACTIVE = 123
    DECK_A_LOOP_OUT = 122
    DECK_A_LOOP_IN_SET_CUE = 121
    DECK_B_LOOP_ACTIVE = 126
    DECK_B_LOOP_OUT = 125
    DECK_B_LOOP_IN_SET_CUE = 124
    DECK_C_LOOP_ACTIVE = 55
    DECK_C_LOOP_OUT = 54
    DECK_C_LOOP_IN_SET_CUE = 53
    DECK_D_LOOP_ACTIVE = 58
    DECK_D_LOOP_OUT = 57

    # =========== FX UNIT 1 (VERIFIED!) ===========
    FX1_UNIT_ON = 96
    FX1_BUTTON_3 = 95
    FX1_BUTTON_2 = 94
    FX1_BUTTON_1 = 93
    FX1_KNOB_3 = 79
    FX1_KNOB_2 = 78
    FX1_KNOB_1 = 77
    FX1_DRY_WET = 76

    # =========== FX UNIT 2 (VERIFIED!) ===========
    FX2_UNIT_ON = 104
    FX2_BUTTON_3 = 103
    FX2_BUTTON_2 = 102
    FX2_BUTTON_1 = 101
    FX2_KNOB_3 = 100
    FX2_KNOB_2 = 99
    FX2_KNOB_1 = 98
    FX2_DRY_WET = 97

    # =========== FX UNIT 3 (VERIFIED!) ===========
    FX3_UNIT_ON = 112
    FX3_BUTTON_3 = 111
    FX3_BUTTON_2 = 110
    FX3_BUTTON_1 = 109
    FX3_KNOB_3 = 108
    FX3_KNOB_2 = 107
    FX3_KNOB_1 = 106
    FX3_DRY_WET = 105

    # =========== FX UNIT 4 (VERIFIED!) ===========
    FX4_UNIT_ON = 120
    FX4_BUTTON_3 = 119
    FX4_BUTTON_2 = 118
    FX4_BUTTON_1 = 117
    FX4_KNOB_3 = 116
    FX4_KNOB_2 = 115
    FX4_KNOB_1 = 114
    FX4_DRY_WET = 113


class TraktorMIDIDriver:
    """
    Main MIDI driver class for Traktor Pro 3 communication

    Args:
        port_name: Nome della porta MIDI (default: auto-detect)
        dry_run: Se True, logga comandi ma NON li invia (safe testing mode)
    """

    def __init__(self, port_name: Optional[str] = None, dry_run: bool = False):
        self.port_name = port_name or self._get_default_port_name()
        self.dry_run = dry_run
        self.midi_out = None
        self.is_connected = False

        if not dry_run:
            self._setup_midi()
        else:
            logger.info("[DRY-RUN] MIDI Driver in modalità simulazione")
            logger.info(f"[DRY-RUN] Porta target: {self.port_name}")
            self.is_connected = True  # Simula connessione per testing

    @staticmethod
    def _get_default_port_name() -> str:
        system = platform.system()
        if system == "Windows":
            return "Traktor MIDI Bus 1"
        elif system == "Darwin":
            return "Driver IAC Bus 1"
        else:
            return "Traktor Virtual Port"

    def _setup_midi(self) -> None:
        try:
            if _USING_MIDO:
                available_ports = mido.get_output_names()
                logger.info(f"Available MIDI ports: {available_ports}")
                port_name_found = None
                for port in available_ports:
                    if self.port_name in port:
                        port_name_found = port
                        break
                if port_name_found is None:
                    raise RuntimeError(f"MIDI port '{self.port_name}' not found")
                self.midi_out = mido.open_output(port_name_found)
                self.is_connected = True
                logger.info(f"Connected to {port_name_found}")
            else:
                self.midi_out = rtmidi.MidiOut()
                available_ports = self.midi_out.get_ports()
                logger.info(f"Available MIDI ports: {available_ports}")
                port_index = None
                for idx, port in enumerate(available_ports):
                    if self.port_name in port:
                        port_index = idx
                        break
                if port_index is None:
                    raise RuntimeError(f"MIDI port '{self.port_name}' not found")
                self.midi_out.open_port(port_index)
                self.is_connected = True
                logger.info(f"Connected to {self.port_name}")
        except Exception as e:
            logger.error(f"Failed to initialize MIDI: {e}")
            raise

    def send_cc(self, cc_number: int, value: int, channel: int = MIDIChannel.AI_CONTROL) -> bool:
        if not (0 <= cc_number <= 127):
            raise ValueError(f"CC number must be 0-127, got {cc_number}")
        if not (0 <= value <= 127):
            raise ValueError(f"Value must be 0-127, got {value}")
        if not (0 <= channel <= 15):
            raise ValueError(f"Channel must be 0-15, got {channel}")

        # DRY-RUN MODE: Log but don't send
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would send → Channel {channel}, CC {cc_number} = {value}")
            return True

        if not self.is_connected or self.midi_out is None:
            logger.error("MIDI not connected")
            return False
        try:
            if _USING_MIDO:
                message = mido.Message('control_change', channel=channel, control=cc_number, value=value)
                self.midi_out.send(message)
            else:
                message = [CONTROL_CHANGE | channel, cc_number, value]
                self.midi_out.send_message(message)
            logger.debug(f"Sent CC: Channel {channel+1}, CC#{cc_number}, Value {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to send MIDI: {e}")
            return False

    def load_track_deck_a(self) -> bool:
        logger.info("Loading track to Deck A...")
        return self.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127, MIDIChannel.AI_CONTROL)

    def play_deck_a(self, play: bool = True) -> bool:
        value = 127 if play else 0
        logger.info(f"{'Playing' if play else 'Pausing'} Deck A...")
        return self.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, value, MIDIChannel.AI_CONTROL)

    def set_deck_a_volume(self, volume: int) -> bool:
        logger.info(f"Setting Deck A volume to {volume}")
        return self.send_cc(TraktorCC.DECK_A_VOLUME, volume, MIDIChannel.AI_CONTROL)

    def sync_deck_a(self, enable: bool = True) -> bool:
        value = 127 if enable else 0
        logger.info(f"{'Enabling' if enable else 'Disabling'} Deck A sync")
        return self.send_cc(TraktorCC.DECK_A_SYNC_ON, value, MIDIChannel.AI_CONTROL)

    def get_available_ports(self) -> List[str]:
        if _USING_MIDO:
            return mido.get_output_names()
        else:
            if self.midi_out is None:
                temp_midi = rtmidi.MidiOut()
                ports = temp_midi.get_ports()
                del temp_midi
                return ports
            return self.midi_out.get_ports()

    def reconnect(self) -> bool:
        logger.info("Attempting to reconnect...")
        try:
            self.close()
            self._setup_midi()
            return self.is_connected
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            return False

    def close(self) -> None:
        if self.midi_out is not None:
            try:
                if _USING_MIDO:
                    self.midi_out.close()
                else:
                    self.midi_out.close_port()
                logger.info("MIDI connection closed")
            except Exception as e:
                logger.warning(f"Error closing MIDI: {e}")
            finally:
                self.is_connected = False
                self.midi_out = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()


if __name__ == "__main__":
    with TraktorMIDIDriver() as driver:
        print(f"Connected to: {driver.port_name}")
        driver.load_track_deck_a()
