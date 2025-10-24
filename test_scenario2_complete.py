#!/usr/bin/env python3
"""
Test Scenario 2 COMPLETO - Second Track Load
Carica secondo track su Deck B mentre Deck A sta suonando.

ASPETTATIVE:
- Deck A continua indisturbato
- Deck B caricato con volume a 0
- Deck B con SYNC enabled
- Deck B suona silenziosamente (pronto per mix)
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from traktor_safety_checks import TraktorSafetyChecks
import time

print("="*70)
print("SCENARIO 2: SECOND TRACK LOAD (Deck A playing)")
print("="*70)
print()
print("PREREQUISITI:")
print("  - Deck A deve avere una traccia che SUONA")
print("  - Se non hai fatto Scenario 1, fallo prima")
print()
print("COSA SUCCEDE:")
print("  1. Deck A continua a suonare (indisturbato)")
print("  2. Deck B viene caricato silenziosamente")
print("  3. Deck B suona a volume 0 (cued, pronto per mix)")
print()

input("Premi ENTER per iniziare Scenario 2...")

midi = TraktorMIDIDriver()
safety = TraktorSafetyChecks(midi)

# Simula Deck A in stato playing (da Scenario 1)
print("\n[SETUP] Marking Deck A as playing (from Scenario 1)")
safety.mark_deck_playing('A', True)
safety.deck_states['A']['is_master'] = True
safety.deck_states['A']['volume'] = safety.SAFE_DEFAULTS['volume_playing']

print("\n[STEP 1] PRE-LOAD SAFETY CHECK (Deck B)")
print("-"*70)
print("PROTEZIONE: Deck A deve rimanere indisturbato!")
safety.pre_load_safety_check('B', opposite_deck_playing=True)

print("\n[STEP 2] LOAD TRACK TO DECK B")
print("-"*70)
print("Seleziona una SECONDA traccia nel browser...")
print("Caricamento tra 3 secondi...")
time.sleep(3)

midi.send_cc(TraktorCC.DECK_B_LOAD_TRACK, 127)
time.sleep(2)

print("\n[STEP 3] POST-LOAD SETUP (Deck B)")
print("-"*70)
print("Configurazione per secondo track (SYNC, non MASTER)")
safety.post_load_safety_setup('B', is_first_track=False)

print("\n[STEP 4] PREPARE FOR PLAYBACK (Deck B - SILENT)")
print("-"*70)
print("Volume rimane a 0% (pronto per fade-in manuale)")
safety.prepare_for_playback('B', is_first_track=False)

print("\n[STEP 5] PLAY DECK B (SILENTLY)")
print("-"*70)
print("Deck B suonera' a volume 0 (cued)")
safety.play_deck_toggle('B')

time.sleep(2)

print()
print("="*70)
print("SCENARIO 2 COMPLETATO!")
print("="*70)
print()
print("VERIFICA in Traktor:")
print()
print("DECK A (non deve essere toccato):")
print("  [ ] Deck A ancora SUONA (waveform si muove)")
print("  [ ] Volume Deck A ancora ~85%")
print("  [ ] Audio Deck A ancora udibile")
print("  [ ] MASTER ancora su Deck A")
print()
print("DECK B (nuovo track):")
print("  [ ] Deck B caricato con nuovo track")
print("  [ ] Deck B SUONA ma SILENZIOSO (waveform si muove, volume 0%)")
print("  [ ] Volume Deck B a 0%")
print("  [ ] EQ Deck B centrati")
print("  [ ] SYNC enabled su Deck B")
print("  [ ] MASTER NOT set su Deck B (AUTO mode)")
print("  [ ] Crossfader posizionato (protegge Deck B)")
print()
print("AUDIO:")
print("  [ ] Senti SOLO Deck A (Deck B e' silenzioso)")
print()

result = input("Tutti i punti verificati? (y/n): ")

if result.lower() == 'y':
    print("\nSUCCESS: Scenario 2 PASSED!")
    print("Deck B e' pronto per essere mixato quando vuoi!")
else:
    print("\nFAIL: Nota quali punti non funzionano")

midi.close()
