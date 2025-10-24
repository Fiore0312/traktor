#!/usr/bin/env python3
"""
Load selected track to Deck A and start playback.
Simple test script for MIDI control.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

def main():
    print("=" * 70)
    print("LOAD AND PLAY - DECK A")
    print("=" * 70)
    print()

    print("[INFO] Assicurati che:")
    print("  1. Traktor sia aperto")
    print("  2. Una traccia sia evidenziata nel browser")
    print("  3. loopMIDI sia in esecuzione")
    print("  4. Traktor usi ASIO (non WASAPI)")
    print()

    input("Premi ENTER per procedere...")
    print()

    # Initialize MIDI driver
    print("[1/4] Connessione MIDI driver...")
    try:
        midi = TraktorMIDIDriver()
        print(f"[OK] Connesso a: {midi.port_name}")
    except Exception as e:
        print(f"[ERROR] Connessione fallita: {e}")
        print()
        print("Verifica:")
        print("  - loopMIDI aperto con 'Traktor MIDI Bus 1'")
        print("  - Traktor aperto e configurato per MIDI")
        return

    print()

    # Load track
    print("[2/4] Caricamento traccia nel Deck A...")
    print(f"      Invio CC {TraktorCC.DECK_A_LOAD_TRACK} = 127")
    midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)

    print("[WAIT] Attendendo caricamento traccia...")
    time.sleep(1.5)  # Wait for track to load
    print("[OK] Traccia dovrebbe essere caricata")
    print()

    # Set volume to reasonable level
    print("[3/4] Impostazione volume Deck A...")
    volume_value = 108  # ~85%
    print(f"      Invio CC {TraktorCC.DECK_A_VOLUME} = {volume_value} (~85%)")
    midi.send_cc(TraktorCC.DECK_A_VOLUME, volume_value)
    print("[OK] Volume impostato")
    print()

    # Play
    print("[4/4] Avvio playback...")
    print(f"      Invio CC {TraktorCC.DECK_A_PLAY_PAUSE} = 127")
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
    print("[OK] PLAY inviato!")
    print()

    print("=" * 70)
    print("COMANDI INVIATI CON SUCCESSO")
    print("=" * 70)
    print()
    print("Dovresti sentire la traccia in riproduzione su Deck A.")
    print()
    print("Verifica in Traktor:")
    print("  - Deck A ha la traccia caricata (waveform visibile)")
    print("  - Deck A sta riproducendo (pulsante PLAY acceso)")
    print("  - Volume fader a ~85%")
    print()

    # Keep playing for a bit
    print("[INFO] Riproduzione in corso...")
    print("      Premi Ctrl+C per fermare e chiudere")
    print()

    try:
        for i in range(10):
            time.sleep(1)
            print(f"      Riproduzione: {i+1}s", end='\r')
        print()
    except KeyboardInterrupt:
        print()
        print("[STOP] Interruzione utente")

    print()
    print("[CLEANUP] Chiusura connessione MIDI...")
    midi.close()
    print("[OK] Connessione chiusa")
    print()
    print("=" * 70)
    print("TEST COMPLETATO")
    print("=" * 70)

if __name__ == "__main__":
    main()
