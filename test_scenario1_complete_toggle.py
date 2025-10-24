#!/usr/bin/env python3
"""
Test Scenario 1 COMPLETO con Toggle Mode
Primo track load con safety layer e Toggle mode per Play/Pause.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from traktor_safety_checks import TraktorSafetyChecks
import time

print("="*70)
print("SCENARIO 1: FIRST TRACK LOAD - COMPLETE TEST")
print("="*70)
print()
print("Safety layer + Toggle mode Play/Pause")
print()
print("Prima di iniziare, seleziona una traccia nel browser Traktor")
print()
input("Premi ENTER quando pronto...")

midi = TraktorMIDIDriver()
safety = TraktorSafetyChecks(midi)

print("\n[STEP 1] PRE-LOAD SAFETY")
print("-"*70)
safety.pre_load_safety_check('A', opposite_deck_playing=False)

print("\n[STEP 2] LOAD TRACK")
print("-"*70)
print("Caricamento tra 2 secondi...")
time.sleep(2)
midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
time.sleep(2)

print("\n[STEP 3] POST-LOAD SETUP")
print("-"*70)
safety.post_load_safety_setup('A', is_first_track=True)

print("\n[STEP 4] PREPARE FOR PLAYBACK")
print("-"*70)
safety.prepare_for_playback('A', is_first_track=True)

print("\n[STEP 5] PLAY (Toggle mode)")
print("-"*70)
safety.play_deck_toggle('A')

time.sleep(2)

print()
print("="*70)
print("TEST COMPLETATO!")
print("="*70)
print()
print("VERIFICA in Traktor:")
print("  [ ] Deck A caricato")
print("  [ ] Deck A SUONA (waveform si muove)")
print("  [ ] Volume ~85%")
print("  [ ] EQ centrati")
print("  [ ] MASTER ON")
print("  [ ] SYNC OFF")
print("  [ ] Crossfader LEFT")
print("  [ ] Audio udibile")
print()

result = input("Tutto OK? (y/n): ")

if result.lower() == 'y':
    print("\nSUCCESS: Scenario 1 PASSED con Toggle mode!")
else:
    print("\nFAIL: Controlla cosa non funziona")

midi.close()
