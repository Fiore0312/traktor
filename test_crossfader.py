#!/usr/bin/env python3
"""
Test Crossfader MIDI Control
Verifica se CC 8 controlla il crossfader in Traktor.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_crossfader_movement():
    """Test movimento crossfader."""
    print("="*70)
    print("TEST CROSSFADER - MIDI CC 8")
    print("="*70)
    print()
    print("Questo test invierà comandi al crossfader.")
    print()
    print("Osserva Traktor GUI:")
    print("  - Il crossfader dovrebbe MUOVERSI")
    print("  - LEFT (0) -> CENTER (64) -> RIGHT (127)")
    print()

    midi = TraktorMIDIDriver()

    print("Inizio test in 2 secondi...")
    time.sleep(2)

    print("\n[TEST 1] Crossfader -> LEFT (value 0)")
    midi.send_cc(8, 0)
    time.sleep(2)

    print("[TEST 2] Crossfader -> CENTER (value 64)")
    midi.send_cc(8, 64)
    time.sleep(2)

    print("[TEST 3] Crossfader -> RIGHT (value 127)")
    midi.send_cc(8, 127)
    time.sleep(2)

    print("[TEST 4] Crossfader -> LEFT (value 0)")
    midi.send_cc(8, 0)
    time.sleep(2)

    print()
    print("="*70)
    print("TEST COMPLETATO")
    print("="*70)
    print()
    print("VERIFICA in Traktor:")
    print("  - Il crossfader si è mosso durante il test?")
    print("  - Se SI: CC 8 è corretto")
    print("  - Se NO: CC 8 non controlla il crossfader")
    print()
    print("Se il crossfader NON si è mosso:")
    print("  1. Apri Traktor > Preferences > Controller Manager")
    print("  2. Trova 'Generic MIDI' device")
    print("  3. Cerca il mapping per 'Mixer > Crossfader'")
    print("  4. Verifica il CC number")
    print("  5. Oppure usa MIDI Learn per mappare CC 8 al crossfader")
    print()

    midi.close()

if __name__ == "__main__":
    test_crossfader_movement()
