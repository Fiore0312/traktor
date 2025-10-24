#!/usr/bin/env python3
"""
Play Deck A - send PLAY command only.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

print("=" * 70)
print("PLAY DECK A")
print("=" * 70)
print()

# Initialize MIDI driver
print("[1/2] Connecting to MIDI...")
try:
    midi = TraktorMIDIDriver()
    print(f"[OK] Connected: {midi.port_name}")
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    exit(1)

print()

# Send PLAY command
print("[2/2] Sending PLAY command to Deck A...")
print(f"      CC {TraktorCC.DECK_A_PLAY_PAUSE} = 127")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
time.sleep(0.1)
print("[OK] PLAY command sent!")
print()

print("=" * 70)
print("DONE")
print("=" * 70)
print()
print("Deck A should now be playing.")
print()

# Cleanup
midi.close()
print("[OK] MIDI closed")
