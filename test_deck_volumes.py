#!/usr/bin/env python3
"""
Test Deck Volumes - Verifica controllo volume Deck A e B
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

def test_volume_controls():
    """Test volume faders su entrambi i deck."""
    print("="*70)
    print("TEST VOLUME CONTROLS - Deck A e Deck B")
    print("="*70)
    print()
    print("Questo test muoverà i volume faders di entrambi i deck.")
    print()
    print("Osserva Traktor GUI:")
    print("  - Volume Deck A dovrebbe muoversi")
    print("  - Volume Deck B dovrebbe muoversi")
    print()

    midi = TraktorMIDIDriver()

    print("Inizio test in 2 secondi...")
    time.sleep(2)

    # Test Deck A Volume (CC 65)
    print("\n--- DECK A VOLUME TEST ---")
    print("[TEST] Deck A Volume -> 0")
    midi.send_cc(TraktorCC.DECK_A_VOLUME, 0)
    time.sleep(2)

    print("[TEST] Deck A Volume -> 64 (50%)")
    midi.send_cc(TraktorCC.DECK_A_VOLUME, 64)
    time.sleep(2)

    print("[TEST] Deck A Volume -> 108 (85%)")
    midi.send_cc(TraktorCC.DECK_A_VOLUME, 108)
    time.sleep(2)

    print("[TEST] Deck A Volume -> 0 (reset)")
    midi.send_cc(TraktorCC.DECK_A_VOLUME, 0)
    time.sleep(2)

    # Test Deck B Volume (CC 60)
    print("\n--- DECK B VOLUME TEST ---")
    print("[TEST] Deck B Volume -> 0")
    midi.send_cc(TraktorCC.DECK_B_VOLUME, 0)
    time.sleep(2)

    print("[TEST] Deck B Volume -> 64 (50%)")
    midi.send_cc(TraktorCC.DECK_B_VOLUME, 64)
    time.sleep(2)

    print("[TEST] Deck B Volume -> 108 (85%)")
    midi.send_cc(TraktorCC.DECK_B_VOLUME, 108)
    time.sleep(2)

    print("[TEST] Deck B Volume -> 0 (reset)")
    midi.send_cc(TraktorCC.DECK_B_VOLUME, 0)
    time.sleep(2)

    print()
    print("="*70)
    print("TEST COMPLETATO")
    print("="*70)
    print()
    print("VERIFICA in Traktor:")
    print("  - Deck A volume fader si è mosso?")
    print("  - Deck B volume fader si è mosso?")
    print()
    print("Se uno dei due NON si è mosso:")
    print("  - Il CC number potrebbe essere sbagliato")
    print("  - Oppure non è mappato in Traktor Controller Manager")
    print()

    midi.close()

if __name__ == "__main__":
    test_volume_controls()
