#!/usr/bin/env python3
"""
Test diagnostico PLAY/PAUSE Deck A
Invia comandi multipli con delay per vedere la risposta.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

print("="*70)
print("TEST DIAGNOSTICO PLAY/PAUSE - DECK A")
print("="*70)
print()
print("Inviero' una sequenza di comandi PLAY/PAUSE")
print("Osserva se Deck A risponde")
print()

midi = TraktorMIDIDriver()

# Test 1: PLAY con valore 127
print("[TEST 1] PLAY (CC 47 = 127)")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
time.sleep(2)
print("  -> Deck A sta suonando? Nota lo stato")
time.sleep(1)

# Test 2: PAUSE con valore 0
print("\n[TEST 2] PAUSE (CC 47 = 0)")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 0)
time.sleep(2)
print("  -> Deck A si e' fermato?")
time.sleep(1)

# Test 3: Di nuovo PLAY
print("\n[TEST 3] PLAY di nuovo (CC 47 = 127)")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
time.sleep(2)
print("  -> Deck A sta suonando ora?")
time.sleep(1)

# Test 4: Toggle (come se fosse Toggle mode)
print("\n[TEST 4] Invio 127 di nuovo (toggle)")
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
time.sleep(2)
print("  -> Cosa e' successo?")

print()
print("="*70)
print("TEST COMPLETATO")
print("="*70)
print()
print("Risultati:")
print("  - Se NESSUN comando ha funzionato: CC 47 non e' mappato")
print("  - Se PLAY=127 non funziona ma 0 si: Interaction Mode sbagliato")
print("  - Se funziona solo al secondo 127: Toggle Mode (sbagliato)")
print("  - Se tutto funziona: Problema nel workflow precedente")
print()

midi.close()
