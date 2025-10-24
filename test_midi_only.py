#!/usr/bin/env python3
"""
Test isolato: solo connessione e invio MIDI.
Nessun vision, nessuna logica complessa, solo driver.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
from traktor_midi_driver import TraktorMIDIDriver
import time


def test_midi_connection():
    """Test connessione MIDI base."""
    print("=" * 70)
    print("TEST MIDI CONNECTION")
    print("=" * 70)
    print()

    try:
        # Init driver
        print("[1/5] Inizializzando MIDI driver...")
        midi = TraktorMIDIDriver()

        if not midi.is_connected:
            print("[ERROR] MIDI NON CONNESSO!")
            print()
            print("Verifica:")
            print("  1. loopMIDI aperto?")
            print("  2. Porta 'Traktor MIDI Bus 1' esiste?")
            print("  3. Traktor aperto?")
            print()
            print("Esegui: python verify_midi_setup.py")
            return False

        print(f"[OK] CONNESSO a: {midi.port_name}")

        # Info setup
        print()
        print("[2/5] Setup verification...")
        print("      Assicurati che:")
        print("      - Traktor sia aperto")
        print("      - TSI mapping sia caricato")
        print("      - Almeno un deck abbia una traccia caricata")

        input("\n      Premi ENTER quando pronto (o Ctrl+C per annullare)...")

        # Test comando sicuro (Master Volume - non invasivo)
        print()
        print("[3/5] Test comando sicuro...")
        print("      Invio: Master Volume (CC 7)")
        print("      Questo NON dovrebbe causare play/stop/load")

        midi.send_cc(7, 100)
        print("[OK] Comando inviato!")
        time.sleep(0.5)

        # Test Play/Pause Deck A (se c'è traccia)
        print()
        print("[4/5] Test Play/Pause Deck A...")
        print("      Invio: CC 0 (Deck A Play/Pause)")
        print("      Se c'è una traccia su Deck A, dovrebbe play/pause")

        input("      Premi ENTER per inviare (o Ctrl+C per skip)...")

        midi.send_cc(0, 127)
        print("[OK] Play/Pause inviato!")

        time.sleep(1)

        # Secondo Play/Pause per stoppare
        print("      Invio secondo comando per stoppare...")
        time.sleep(1)
        midi.send_cc(0, 127)
        print("[OK] Stop inviato!")

        # Test completato
        print()
        print("[5/5] Cleanup...")
        midi.close()
        print("[OK] MIDI connection closed")

        return True

    except KeyboardInterrupt:
        print()
        print("[WARN] Test interrotto dall'utente")
        return False
    except Exception as e:
        print()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    success = test_midi_connection()

    print()
    print("=" * 70)
    if success:
        print("[OK] TEST MIDI: PASSED")
        print("=" * 70)
        print()
        print("Driver MIDI funziona correttamente!")
        print()
        print("Prossimi passi:")
        print("  1. Se Deck A ha reagito ai comandi: tutto OK")
        print("  2. Procedi con: python demo_manual_analysis.py")
    else:
        print("[FAIL] TEST MIDI: FAILED")
        print("=" * 70)
        print()
        print("Risolvi i problemi MIDI prima di procedere!")
        print("Esegui: python verify_midi_setup.py")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
