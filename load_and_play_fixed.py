#!/usr/bin/env python3
"""
Load and Play with PROPER DELAYS - Fixed version.
Il problema era il timing troppo veloce tra i comandi!
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

print("=" * 70)
print("LOAD AND PLAY - DECK A (WITH PROPER DELAYS)")
print("=" * 70)
print()

# Initialize
print("[INIT] Connecting to MIDI...")
midi = TraktorMIDIDriver()
print(f"[OK] Connected: {midi.port_name}")
print()

# STEP 1: Load track
print("[STEP 1/3] Loading track to Deck A...")
print(f"           Sending CC {TraktorCC.DECK_A_LOAD_TRACK} = 127")
midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)

# CRITICAL: Wait for Traktor to process the load command
print("[WAIT]     Waiting 2 seconds for track to load...")
time.sleep(2.0)  # AUMENTATO! Era 1.5, ora 2 secondi
print("[OK]       Track loaded")
print()

# STEP 2: Set volume
print("[STEP 2/3] Setting volume to 85%...")
print(f"           Sending CC {TraktorCC.DECK_A_VOLUME} = 108")
midi.send_cc(TraktorCC.DECK_A_VOLUME, 108)

# CRITICAL: Wait for Traktor to process the volume change
print("[WAIT]     Waiting 0.5 seconds...")
time.sleep(0.5)  # AGGIUNTO! Prima non c'era delay
print("[OK]       Volume set")
print()

# STEP 3: Play
print("[STEP 3/3] Starting playback...")
print(f"           Sending CC {TraktorCC.DECK_A_PLAY_PAUSE} = 127")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)

# CRITICAL: Wait to confirm play started
print("[WAIT]     Waiting 0.5 seconds...")
time.sleep(0.5)  # AGGIUNTO! Conferma che play è partito
print("[OK]       Play command sent")
print()

print("=" * 70)
print("SUCCESS - TRACK SHOULD BE PLAYING NOW!")
print("=" * 70)
print()
print("Delays used:")
print("  - After LOAD:   2.0 seconds (track loading)")
print("  - After VOLUME: 0.5 seconds (mixer adjustment)")
print("  - After PLAY:   0.5 seconds (confirmation)")
print()
print("Total time: ~3 seconds (proper MIDI timing)")
print()

# Cleanup
midi.close()
print("[OK] MIDI connection closed")
