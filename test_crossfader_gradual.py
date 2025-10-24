#!/usr/bin/env python3
"""
Test Crossfader - Movimento GRADUALE
Invia valori incrementali piccoli per vedere se il browser reagisce.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_gradual_movement():
    """Test con movimento graduale del crossfader."""
    print("="*70)
    print("TEST CROSSFADER - MOVIMENTO GRADUALE")
    print("="*70)
    print()
    print("Questo test muovera' il crossfader LENTAMENTE da LEFT a RIGHT")
    print("con piccoli incrementi di 1 unita' alla volta.")
    print()
    print("Osserva:")
    print("  - Crossfader dovrebbe muoversi lentamente da sinistra a destra")
    print("  - Browser dovrebbe rimanere FERMO")
    print()
    input("Premi ENTER per iniziare...")

    midi = TraktorMIDIDriver()

    print("\n[TEST] Movimento da LEFT (0) a RIGHT (127) - incrementi di 1")
    print("Durata: ~12 secondi")
    print()

    # Start from LEFT
    current_value = 0
    midi.send_cc(56, current_value)
    time.sleep(1)

    # Gradual movement to RIGHT
    while current_value < 127:
        current_value += 1
        midi.send_cc(56, current_value)
        time.sleep(0.1)  # 100ms tra ogni step

    print("\n[COMPLETATO] Crossfader ora dovrebbe essere a RIGHT (127)")
    print()
    print("Cosa hai osservato?")
    print("  1. Solo crossfader si e' mosso (browser fermo)")
    print("  2. Crossfader E browser si sono mossi")
    print("  3. Solo browser si e' mosso")
    print()

    response = input("Scegli (1/2/3): ")

    midi.close()

    print()
    if response == '1':
        print("✅ OTTIMO! Il problema e' nei salti bruschi di valore!")
        print("   Soluzione: Usare transizioni graduali nel safety layer")
    elif response == '2':
        print("⚠️ PROBLEMA: Anche con movimento graduale il browser si muove")
        print("   Potrebbe esserci un mapping nascosto o conflitto")
    else:
        print("❌ ERRORE: CC 56 non controlla il crossfader!")

if __name__ == "__main__":
    test_gradual_movement()
