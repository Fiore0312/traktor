#!/usr/bin/env python3
"""
MIDI Learn Test - Send repeated MIDI signals for learning.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

print("=" * 70)
print("MIDI LEARN TEST - PLAY BUTTON")
print("=" * 70)
print()
print("ISTRUZIONI:")
print("  1. In Traktor: vai in Preferences > Controller Manager")
print("  2. Seleziona il tuo device Generic MIDI")
print("  3. Trova 'Deck A > Play/Pause' nella lista")
print("  4. Clicca sul campo 'Assignment' per entrare in MIDI Learn mode")
print("  5. Questo script inviera CC 47 ripetutamente")
print("  6. Traktor mostrera quale CC riceve")
print()
print("PRONTO? Script inizia in 3 secondi...")
time.sleep(3)
print()

# Initialize
midi = TraktorMIDIDriver()
print(f"[OK] Connected: {midi.port_name}")
print()

print("=" * 70)
print("SENDING MIDI LEARN SIGNAL")
print("=" * 70)
print()
print("Invio CC 47 (DECK_A_PLAY_PAUSE) ripetutamente...")
print("Controlla in Traktor quale CC viene rilevato!")
print()
print("Premi Ctrl+C per fermare")
print()

try:
    count = 0
    while True:
        count += 1

        # Send CC 47 on channel 0
        midi.send_cc(47, 127, channel=0)
        print(f"[{count:3d}] Sent: Channel 0, CC 47, Value 127", end='\r')

        time.sleep(0.5)  # 2 Hz

        # Toggle value for visibility
        midi.send_cc(47, 0, channel=0)
        time.sleep(0.5)

except KeyboardInterrupt:
    print()
    print()
    print("[STOP] Test interrotto")

print()
print("=" * 70)
print("RISULTATI")
print("=" * 70)
print()
print("Cosa ha rilevato Traktor in MIDI Learn?")
print()
print("Se ha mostrato:")
print("  - 'CC 47' > Perfetto! Il mapping e corretto")
print("  - Altro CC > Dobbiamo usare quel CC invece di 47")
print("  - Nulla > MIDI non arriva, problema di routing")
print()

midi.close()
print("[OK] MIDI closed")
