#!/usr/bin/env python3
"""
Debug CC 56 - Trova la soglia esatta dove inizia il conflitto
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_specific_values():
    """Test valori specifici per trovare la soglia del problema."""
    print("="*70)
    print("DEBUG CC 56 - RICERCA SOGLIA CONFLITTO")
    print("="*70)
    print()
    print("Inviero' CC 56 con valori specifici e pausa tra ognuno.")
    print("Nota quale elemento e' selezionato nel browser tree PRIMA di iniziare.")
    print()

    midi = TraktorMIDIDriver()

    # Reset crossfader a sinistra
    print("[RESET] Posiziono crossfader a LEFT (0)")
    midi.send_cc(56, 0)
    time.sleep(2)

    # Test values around the threshold
    test_values = [
        (0, "LEFT - baseline"),
        (32, "25% - low range"),
        (50, "39% - approaching center"),
        (60, "47% - near center"),
        (64, "50% - CENTER exact"),
        (68, "53% - just past center"),
        (70, "55% - past center"),
        (75, "59% - mid-high range"),
        (80, "63% - high range"),
        (90, "71% - higher"),
        (100, "79% - approaching right"),
        (127, "100% - RIGHT"),
    ]

    print("\nOsserva il browser tree. Segna a quale valore INIZIA a muoversi:")
    print()

    for value, description in test_values:
        print(f"[TEST] CC 56 = {value:3d} ({description})")
        midi.send_cc(56, value)
        time.sleep(3)  # Lunga pausa per osservare

    print()
    print("="*70)
    print("ANALISI COMPLETATA")
    print("="*70)
    print()
    print("A quale valore il browser tree ha iniziato a muoversi?")
    print("  - Se < 64: Problema nel range basso")
    print("  - Se = 64: Conflitto esatto a CENTER")
    print("  - Se > 64: Problema nel range alto")
    print("  - Se MAI: Forse dipende dalla velocita' di cambio")
    print()

    midi.close()

if __name__ == "__main__":
    test_specific_values()
