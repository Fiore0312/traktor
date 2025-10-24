#!/usr/bin/env python3
"""
Test Crossfader - UN VALORE ALLA VOLTA
Invia solo un comando CC 56 per verificare il comportamento.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_single_value(value):
    """Test con un singolo valore."""
    print(f"\n[TEST] Invio CC 56 = {value}")
    print(f"Osserva Traktor:")
    print(f"  - Il crossfader dovrebbe andare a {value}/127")
    print(f"  - Il browser NON dovrebbe muoversi")
    print()

    midi = TraktorMIDIDriver()

    time.sleep(1)
    midi.send_cc(56, value)

    time.sleep(2)

    midi.close()

    response = input("Cosa si e' mosso? (c=solo crossfader, b=solo browser, cb=entrambi): ")
    return response

def main():
    print("="*70)
    print("TEST CROSSFADER - SINGOLI VALORI CC 56")
    print("="*70)
    print()
    print("Prima di iniziare:")
    print("  1. Osserva la posizione attuale del crossfader")
    print("  2. Osserva quale elemento e' selezionato nel browser tree")
    print()
    input("Premi ENTER per iniziare...")

    results = []

    # Test 1: Value 0 (LEFT)
    print("\n--- TEST 1: CC 56 = 0 (LEFT) ---")
    result1 = test_single_value(0)
    results.append(("0 (LEFT)", result1))

    input("\nPremi ENTER per test successivo...")

    # Test 2: Value 127 (RIGHT)
    print("\n--- TEST 2: CC 56 = 127 (RIGHT) ---")
    result2 = test_single_value(127)
    results.append(("127 (RIGHT)", result2))

    input("\nPremi ENTER per test successivo...")

    # Test 3: Value 64 (CENTER)
    print("\n--- TEST 3: CC 56 = 64 (CENTER) ---")
    result3 = test_single_value(64)
    results.append(("64 (CENTER)", result3))

    # Summary
    print("\n" + "="*70)
    print("RISULTATI TEST")
    print("="*70)
    for value, result in results:
        print(f"CC 56 = {value:12} -> {result}")

    print()
    print("Analisi:")
    if all(r == 'c' for _, r in results):
        print("  ✅ PERFETTO! Solo crossfader si muove")
    elif all(r == 'cb' for _, r in results):
        print("  ⚠️ PROBLEMA: Entrambi si muovono sempre")
        print("     Possibile: Mapping duplicato o conflitto Traktor")
    elif all(r == 'b' for _, r in results):
        print("  ❌ ERRORE: Solo browser si muove!")
        print("     CC 56 NON controlla il crossfader")
    else:
        print("  🤔 COMPORTAMENTO INCONSISTENTE")
        print("     Dipende dal valore inviato")

if __name__ == "__main__":
    main()
