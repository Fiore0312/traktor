#!/usr/bin/env python3
"""
Demo loop manuale: Screenshot → Analisi Claude → Decisione → MIDI
Questa è la versione "human-in-the-loop" per capire il workflow.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
from autonomous_dj.generated.traktor_vision import TraktorVisionSystem
from traktor_midi_driver import TraktorMIDIDriver
import time


def manual_vision_loop():
    """Loop interattivo per testare vision-guided workflow."""
    print("=" * 70)
    print("DEMO: MANUAL VISION-GUIDED LOOP")
    print("=" * 70)
    print()
    print("Questo script ti permette di:")
    print("  1. Catturare screenshot di Traktor")
    print("  2. Analizzarli manualmente (tu guardi e decidi)")
    print("  3. Inviare comandi MIDI basati sulla tua analisi")
    print("  4. Verificare il risultato con nuovo screenshot")
    print()

    # Init (dry_run per sicurezza)
    print("[INIT] Inizializzando sistemi...")
    vision = TraktorVisionSystem()
    midi = TraktorMIDIDriver(dry_run=True)  # SAFE: solo log

    print("[OK] Sistemi inizializzati (MIDI in DRY-RUN mode)")
    print("     Per inviare comandi reali, modifica: dry_run=False")
    print()

    iteration = 0
    try:
        while True:
            iteration += 1
            print()
            print("=" * 70)
            print(f"ITERATION {iteration}")
            print("=" * 70)

            # Step 1: Capture
            print()
            print("[1/4] Catturando screenshot...")
            screenshot_path = vision.capture_traktor_window()
            print(f"      Salvato: {screenshot_path}")

            # Step 2: Analisi manuale
            print()
            print("[2/4] ANALISI MANUALE")
            print(f"      Apri: {screenshot_path}")
            print("      Guarda lo screenshot e rispondi:")

            input("\n      Premi ENTER quando hai visto lo screenshot...")

            print()
            print("      Cosa vedi?")
            print("      a) Track evidenziata nel browser, Deck A vuoto")
            print("      b) Track evidenziata nel browser, Deck B vuoto")
            print("      c) Necessario navigare browser (scroll list)")
            print("      d) Necessario navigare cartelle (tree)")
            print("      e) Deck pronto per play")
            print("      f) Comando custom")
            print("      q) Quit")

            choice = input("\n      Scelta: ").lower().strip()

            if choice == 'q':
                print("\n[EXIT] Uscita dal loop")
                break

            # Step 3: Decisione e comando MIDI
            print()
            print("[3/4] COMANDO MIDI")

            if choice == 'a':
                print("      Action: Load to Deck A")
                print("      CC: 43 (DECK_A_LOAD_TRACK)")
                midi.send_cc(43, 127)
            elif choice == 'b':
                print("      Action: Load to Deck B")
                print("      CC: 52 (DECK_B_LOAD_TRACK)")
                midi.send_cc(52, 127)
            elif choice == 'c':
                print("      Action: Scroll browser list")
                print("      CC: 74 (BROWSER_SCROLL_LIST)")
                direction = input("      Direction (up/down): ").lower()
                value = 64 if direction == 'down' else 63
                midi.send_cc(74, value)
            elif choice == 'd':
                print("      Action: Navigate folder tree")
                print("      CC: 72 (BROWSER_SCROLL_TREE_INC)")
                direction = input("      Direction (up/down): ").lower()
                cc = 72 if direction == 'down' else 73
                midi.send_cc(cc, 127)
            elif choice == 'e':
                print("      Action: Play Deck A")
                print("      CC: 0 (DECK_A_PLAY_PAUSE)")
                midi.send_cc(0, 127)
            elif choice == 'f':
                print("      Custom command")
                cc = input("      CC number: ")
                val = input("      Value (0-127): ")
                try:
                    midi.send_cc(int(cc), int(val))
                except ValueError:
                    print("      [ERROR] Input invalido")
            else:
                print("      [SKIP] Scelta non riconosciuta")

            # Step 4: Wait e verifica
            print()
            print("[4/4] ATTESA (simula Traktor che processa)")
            time.sleep(2)

            print()
            print("[INFO] READY per nuova iterazione")
            print("       Nel workflow automatico, Claude:")
            print("       - Vedrebbe questo screenshot")
            print("       - Deciderebbe il comando MIDI")
            print("       - Verificherebbe con nuovo screenshot")

            cont = input("\n       Continuare? (y/n): ").lower()
            if cont != 'y':
                break

    except KeyboardInterrupt:
        print()
        print()
        print("[INTERRUPTED] Loop interrotto dall'utente")

    finally:
        print()
        print("=" * 70)
        print("[CLEANUP] Chiusura connessioni...")
        midi.close()
        print("[OK] Demo completata!")
        print("=" * 70)
        print()
        print("Hai visto il workflow vision-guided in azione:")
        print("  - Screenshot capture (multi-screen)")
        print("  - Analisi visiva (manuale per ora)")
        print("  - Decisione comandi MIDI")
        print("  - Feedback loop")
        print()
        print("Prossimo passo: Integrazione con analisi Claude automatica")


def main():
    """Main entry point."""
    try:
        manual_vision_loop()
    except Exception as e:
        print()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
