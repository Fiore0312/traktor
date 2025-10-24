#!/usr/bin/env python3
"""
Test Crossfader - Test Range Specifici
Verifica se il problema si presenta solo con valori alti.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_range(start, end, description):
    """Test un range specifico di valori."""
    print(f"\n[TEST] {description}")
    print(f"Range: {start} → {end}")
    print("Osserva cosa si muove...")
    print()

    midi = TraktorMIDIDriver()

    time.sleep(1)

    # Set initial position
    midi.send_cc(56, start)
    time.sleep(1)

    # Gradual movement
    current = start
    direction = 1 if end > start else -1

    while (direction > 0 and current <= end) or (direction < 0 and current >= end):
        midi.send_cc(56, current)
        time.sleep(0.05)  # 50ms between steps
        current += direction

    print(f"[COMPLETATO] Crossfader dovrebbe essere a {end}")

    midi.close()

    time.sleep(1)

def main():
    print("="*70)
    print("TEST CROSSFADER - ANALISI RANGE VALORI")
    print("="*70)
    print()
    print("Testeremo 3 range separati:")
    print("  1. LOW range (0-64) - Solo LEFT half")
    print("  2. HIGH range (64-127) - Solo RIGHT half")
    print("  3. FULL range (0-127) - Completo")
    print()
    print("Per ogni test, osserva se il browser tree si muove.")
    print()

    time.sleep(2)

    # Test 1: LOW range (0-64)
    print("\n" + "="*70)
    print("TEST 1: LOW RANGE (0-64)")
    print("="*70)
    test_range(0, 64, "LEFT → CENTER")

    response1 = input("\nBrowser tree si e' mosso? (y/n): ")

    time.sleep(2)

    # Test 2: HIGH range (64-127)
    print("\n" + "="*70)
    print("TEST 2: HIGH RANGE (64-127)")
    print("="*70)
    test_range(64, 127, "CENTER → RIGHT")

    response2 = input("\nBrowser tree si e' mosso? (y/n): ")

    time.sleep(2)

    # Test 3: FULL range back
    print("\n" + "="*70)
    print("TEST 3: FULL RANGE REVERSE (127-0)")
    print("="*70)
    test_range(127, 0, "RIGHT → LEFT (completo)")

    response3 = input("\nBrowser tree si e' mosso? (y/n): ")

    # Summary
    print("\n" + "="*70)
    print("RISULTATI")
    print("="*70)
    print(f"Range 0-64 (LOW):    Browser moved = {response1}")
    print(f"Range 64-127 (HIGH): Browser moved = {response2}")
    print(f"Range 127-0 (FULL):  Browser moved = {response3}")
    print()

    if response1.lower() == 'n' and response2.lower() == 'y':
        print("✅ CONFERMATO: Il problema e' nei valori > 64!")
        print()
        print("Soluzione possibile:")
        print("  1. Usa solo range 0-64 per crossfader (mappato a LEFT half)")
        print("  2. Oppure trova un altro CC libero per crossfader")
        print("  3. Oppure disabilita browser tree navigation")
    elif response1.lower() == 'y' or response2.lower() == 'y':
        print("⚠️ PROBLEMA: Browser si muove in entrambi i range")
        print("   Conflitto di mapping piu' profondo")
    else:
        print("🤔 Browser non si e' mosso in nessun test?")
        print("   Forse dipende dalla velocita' del movimento")

if __name__ == "__main__":
    main()
