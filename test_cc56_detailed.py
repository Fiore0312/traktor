#!/usr/bin/env python3
"""
Test dettagliato CC 56 - Verifica cosa controlla esattamente
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_cc56_detailed():
    """Test specifico per CC 56 con valori incrementali."""
    print("="*70)
    print("TEST DETTAGLIATO CC 56")
    print("="*70)
    print()
    print("Invio valori incrementali di CC 56.")
    print("Osserva ATTENTAMENTE cosa si muove in Traktor:")
    print("  - Solo crossfader?")
    print("  - Solo browser tree?")
    print("  - Entrambi?")
    print()

    midi = TraktorMIDIDriver()

    print("Inizio test in 2 secondi...")
    time.sleep(2)

    # Test con valori incrementali
    values = [0, 32, 64, 96, 127]

    for value in values:
        percentage = int((value / 127) * 100)
        print(f"\n[TEST] CC 56 = {value} ({percentage}%)")
        midi.send_cc(56, value)
        time.sleep(3)  # Pausa lunga per osservare

        input(f"  -> Cosa si e' mosso? (Premi ENTER per continuare)")

    print()
    print("="*70)
    print("TEST COMPLETATO")
    print("="*70)
    print()
    print("Basandoci sulle tue osservazioni:")
    print("  - Se solo crossfader: OK, nessun conflitto reale")
    print("  - Se solo browser: CC sbagliato per crossfader")
    print("  - Se entrambi: conflitto reale da risolvere")
    print()

    midi.close()

if __name__ == "__main__":
    test_cc56_detailed()
