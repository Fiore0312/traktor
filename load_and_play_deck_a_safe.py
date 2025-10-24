#!/usr/bin/env python3
"""
Load and Play Deck A - CON SAFETY LAYER
Workflow completo sicuro per primo track.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
from traktor_safety_checks import TraktorSafetyChecks
import time

def safe_load_and_play_deck_a():
    """Carica e fa partire traccia su Deck A con safety checks."""

    print("="*70)
    print("LOAD AND PLAY DECK A - SAFE WORKFLOW")
    print("="*70)
    print()
    print("Questo workflow usa il safety layer per garantire:")
    print("  - Volume a 0 prima del load")
    print("  - Crossfader posizionato a sinistra")
    print("  - EQ reset a neutral dopo load")
    print("  - MASTER enabled")
    print("  - Volume alzato a 85% prima del play")
    print()

    midi = TraktorMIDIDriver()
    safety = TraktorSafetyChecks(midi)

    print("\n[STEP 1] PRE-LOAD SAFETY CHECK")
    print("-"*70)
    if not safety.pre_load_safety_check('A', opposite_deck_playing=False):
        print("[ERROR] Pre-load check failed!")
        midi.close()
        return

    print("\n[STEP 2] LOAD TRACK")
    print("-"*70)
    print("Seleziona una traccia nel browser di Traktor...")
    print("Inviero' comando LOAD tra 3 secondi...")
    time.sleep(3)

    print("[ACTION] Loading track to Deck A...")
    midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)

    print("[WAIT] Waiting for track to load...")
    time.sleep(2)

    print("\n[STEP 3] POST-LOAD SAFETY SETUP")
    print("-"*70)
    safety.post_load_safety_setup('A', is_first_track=True)

    print("\n[STEP 4] PREPARE FOR PLAYBACK")
    print("-"*70)
    safety.prepare_for_playback('A', is_first_track=True)

    print("\n[STEP 5] PLAY")
    print("-"*70)
    print("[ACTION] Starting playback...")
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
    safety.mark_deck_playing('A', True)

    time.sleep(1)

    print()
    print("="*70)
    print("WORKFLOW COMPLETATO!")
    print("="*70)
    print()
    print("Verifica in Traktor:")
    print("  [OK] Deck A ha track caricato?")
    print("  [OK] Deck A sta suonando (waveform si muove)?")
    print("  [OK] Volume fader Deck A e' a ~85%?")
    print("  [OK] EQ knobs sono centrati (12 o'clock)?")
    print("  [OK] MASTER e' enabled su Deck A?")
    print("  [OK] SYNC e' disabled su Deck A?")
    print("  [OK] Crossfader e' a SINISTRA?")
    print("  [OK] Senti audio?")
    print()

    midi.close()

if __name__ == "__main__":
    safe_load_and_play_deck_a()
