#!/usr/bin/env python3
"""
Test granulare per identificare quale comando causa interferenza.
Test ogni comando MIDI in completo isolamento.
"""
from traktor_midi_driver import TraktorMIDIDriver
import time

def test_single_command_isolation():
    """Test ogni comando in completo isolamento."""

    print("="*70)
    print("TEST ISOLAMENTO COMANDI - DEBUG INTERFERENCE")
    print("="*70)
    print()
    print("Questo test inviera' comandi MIDI uno alla volta")
    print("con lunga pausa per osservare effetti collaterali.")
    print()

    midi = TraktorMIDIDriver()

    tests = [
        {
            'name': 'Crossfader LEFT',
            'action': lambda: midi.send_cc(56, 0),
            'expect': 'Crossfader va a SINISTRA',
            'must_not': 'Browser scrolla'
        },
        {
            'name': 'Crossfader CENTER',
            'action': lambda: midi.send_cc(56, 64),
            'expect': 'Crossfader va al CENTRO',
            'must_not': 'Browser scrolla'
        },
        {
            'name': 'Crossfader RIGHT',
            'action': lambda: midi.send_cc(56, 127),
            'expect': 'Crossfader va a DESTRA',
            'must_not': 'Browser scrolla'
        },
        {
            'name': 'Browser Tree Down',
            'action': lambda: midi.send_cc(72, 1),
            'expect': 'Browser scrolla GIU',
            'must_not': 'Crossfader si muove'
        },
        {
            'name': 'Browser Tree Up',
            'action': lambda: midi.send_cc(73, 1),
            'expect': 'Browser scrolla SU',
            'must_not': 'Crossfader si muove'
        },
    ]

    results = {}

    for i, test in enumerate(tests, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(tests)}: {test['name']}")
        print('='*70)
        print(f"\nCOSA DEVE SUCCEDERE:")
        print(f"  [OK] {test['expect']}")
        print(f"  [NO] {test['must_not']} (SE SUCCEDE = BUG)")
        print()

        input("Premi ENTER per inviare comando... (guarda Traktor)")

        # Send command
        test['action']()

        time.sleep(2)

        # User verification
        print()
        print("OSSERVAZIONE:")
        expect_ok = input(f"  {test['expect']}? (y/n): ").lower() == 'y'
        side_effect = input(f"  {test['must_not']}? (y/n): ").lower() == 'y'

        results[test['name']] = {
            'expected_ok': expect_ok,
            'has_side_effect': side_effect
        }

        if side_effect:
            print()
            print("  WARNING: SIDE EFFECT RILEVATO!")
            print(f"     {test['name']} causa: {test['must_not']}")

    # Report
    print(f"\n{'='*70}")
    print("REPORT INTERFERENZE")
    print('='*70)

    problems = []
    for name, result in results.items():
        if result['has_side_effect']:
            problems.append(name)
            print(f"[FAIL] {name}")
            print(f"       -> Causa side effect indesiderato")
        elif not result['expected_ok']:
            print(f"[WARN] {name}")
            print(f"       -> Non esegue azione attesa")
        else:
            print(f"[OK]   {name}")

    if problems:
        print()
        print("COMANDI CON INTERFERENZA:")
        for p in problems:
            print(f"  - {p}")
        print()
        print("PROSSIMI STEP:")
        print("1. Verifica keyboard shortcuts in Traktor")
        print("2. Disabilita Generic Keyboard device")
        print("3. Controlla se ci sono controller fisici collegati")
    else:
        print()
        print("OK: Nessuna interferenza rilevata nei test!")
        print("   Il problema potrebbe essere intermittente")
        print("   o legato alla velocita' di invio comandi")

    midi.close()

if __name__ == "__main__":
    test_single_command_isolation()
