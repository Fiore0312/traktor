#!/usr/bin/env python3
"""
Test Crossfader - Movimento GRADUALE (Auto)
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_gradual_movement():
    """Test con movimento graduale del crossfader."""
    print("="*70)
    print("TEST CROSSFADER - MOVIMENTO GRADUALE")
    print("="*70)
    print()
    print("Movimento da LEFT (0) a RIGHT (127) - incrementi di 1")
    print("Durata: ~12 secondi")
    print()
    print("OSSERVA ATTENTAMENTE:")
    print("  - Crossfader dovrebbe muoversi LENTAMENTE da sinistra a destra")
    print("  - Browser dovrebbe rimanere COMPLETAMENTE FERMO")
    print()

    midi = TraktorMIDIDriver()

    time.sleep(2)

    print("[AVVIO] Movimento graduale...")

    # Start from LEFT
    current_value = 0
    midi.send_cc(56, current_value)
    time.sleep(1)

    # Gradual movement to RIGHT
    while current_value < 127:
        current_value += 1
        midi.send_cc(56, current_value)
        time.sleep(0.1)  # 100ms tra ogni step
        if current_value % 20 == 0:
            print(f"  -> {current_value}/127")

    print("\n[COMPLETATO] Crossfader dovrebbe essere a RIGHT (127)")
    print()
    print("Verifica in Traktor:")
    print("  - Crossfader e' a destra?")
    print("  - Browser tree e' rimasto fermo?")
    print()

    midi.close()

if __name__ == "__main__":
    test_gradual_movement()
