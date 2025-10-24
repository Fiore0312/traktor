#!/usr/bin/env python3
"""
Test Crossfader MIDI Control - CC 56
Verifica se CC 56 controlla il crossfader in Traktor.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_crossfader_cc56():
    """Test movimento crossfader con CC 56."""
    print("="*70)
    print("TEST CROSSFADER - MIDI CC 56")
    print("="*70)
    print()
    print("Questo test invierà comandi al crossfader usando CC 56.")
    print()
    print("Osserva Traktor GUI:")
    print("  - Il crossfader dovrebbe MUOVERSI")
    print("  - LEFT (0) -> CENTER (64) -> RIGHT (127)")
    print()

    midi = TraktorMIDIDriver()

    print("Inizio test in 2 secondi...")
    time.sleep(2)

    print("\n[TEST 1] Crossfader -> LEFT (value 0)")
    midi.send_cc(56, 0)
    time.sleep(2)

    print("[TEST 2] Crossfader -> CENTER (value 64)")
    midi.send_cc(56, 64)
    time.sleep(2)

    print("[TEST 3] Crossfader -> RIGHT (value 127)")
    midi.send_cc(56, 127)
    time.sleep(2)

    print("[TEST 4] Crossfader -> LEFT (value 0)")
    midi.send_cc(56, 0)
    time.sleep(2)

    print()
    print("="*70)
    print("TEST COMPLETATO")
    print("="*70)
    print()
    print("VERIFICA in Traktor:")
    print("  - Il crossfader si e' mosso durante il test?")
    print("  - Se SI: CC 56 e' CORRETTO! Aggiornero' il mapping")
    print("  - Se NO: Verifica Controller Manager")
    print()

    midi.close()

if __name__ == "__main__":
    test_crossfader_cc56()
