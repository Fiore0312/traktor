#!/usr/bin/env python3
"""
Force PLAY on Deck A - try multiple times with different approaches.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC, MIDIChannel
import time

print("=" * 70)
print("FORCE PLAY DECK A - MULTIPLE ATTEMPTS")
print("=" * 70)
print()

# Initialize
midi = TraktorMIDIDriver()
print(f"[OK] Connected: {midi.port_name}")
print()

# Try different approaches
print("[1] Standard PLAY command (Channel 0, CC 47)...")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127, channel=0)
time.sleep(0.5)

print("[2] PLAY command on Channel 1...")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127, channel=1)
time.sleep(0.5)

print("[3] PLAY toggle (0 then 127)...")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 0, channel=0)
time.sleep(0.2)
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127, channel=0)
time.sleep(0.5)

print("[4] Alternative PLAY CC (if mapped differently)...")
# Try CC 0 which is also sometimes used for play/pause
midi.send_cc(0, 127, channel=0)
time.sleep(0.5)

print()
print("[OK] All commands sent!")
print()
print("If Deck A is still not playing, the issue is likely:")
print("  1. MIDI mapping not loaded in Traktor")
print("  2. Wrong TSI file active")
print("  3. MIDI Learn needed for CC 47")
print()

midi.close()
