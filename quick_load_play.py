#!/usr/bin/env python3
"""
Quick load and play - no interaction required.
Loads selected track to Deck A and plays immediately.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

print("=" * 70)
print("QUICK LOAD AND PLAY - DECK A")
print("=" * 70)
print()

# Initialize MIDI driver
print("[1/4] Connecting to MIDI...")
try:
    midi = TraktorMIDIDriver()
    print(f"[OK] Connected: {midi.port_name}")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    print("\nCheck:")
    print("  - loopMIDI running with 'Traktor MIDI Bus 1'")
    print("  - Traktor open and MIDI configured")
    exit(1)

print()

# Load track
print("[2/4] Loading track to Deck A...")
print(f"      Sending CC {TraktorCC.DECK_A_LOAD_TRACK} = 127")
midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)

print("[WAIT] Waiting for track load...")
time.sleep(1.5)
print("[OK] Track should be loaded")
print()

# Set volume
print("[3/4] Setting Deck A volume...")
volume_value = 108  # ~85%
print(f"      Sending CC {TraktorCC.DECK_A_VOLUME} = {volume_value} (~85%)")
midi.send_cc(TraktorCC.DECK_A_VOLUME, volume_value)
print("[OK] Volume set")
print()

# Play
print("[4/4] Starting playback...")
print(f"      Sending CC {TraktorCC.DECK_A_PLAY_PAUSE} = 127")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
print("[OK] PLAY command sent!")
print()

print("=" * 70)
print("COMMANDS SENT SUCCESSFULLY")
print("=" * 70)
print()
print("Check Traktor:")
print("  - Deck A has track loaded (waveform visible)")
print("  - Deck A is playing (PLAY button lit)")
print("  - Volume fader at ~85%")
print()
print("Track should be playing now!")
print()

# Cleanup
midi.close()
print("[OK] MIDI connection closed")
