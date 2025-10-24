#!/usr/bin/env python3
"""
Analizza Generic Keyboard assignments in Traktor.
Documenta overlap tra keyboard shortcuts e MIDI commands.
"""

def analyze_keyboard_conflicts():
    """Guida per documentare keyboard mapping."""

    print("="*70)
    print("ANALISI KEYBOARD ASSIGNMENTS")
    print("="*70)
    print()
    print("In Traktor Controller Manager:")
    print("1. Seleziona 'Generic Keyboard' (se presente)")
    print("2. Guarda la tabella Assignment")
    print()
    print("Per OGNI riga, annota:")
    print("  - Key (es. 'Arrow Up', 'Shift+A', etc)")
    print("  - Assignment (es. 'Browser.Tree.Scroll')")
    print("  - Target (es. 'Global', 'Deck A', etc)")
    print()
    print("Digita 'done' quando hai finito")
    print()

    assignments = []

    while True:
        print(f"\nAssignment #{len(assignments)+1}")
        key = input("  Key (o 'done' per finire): ")
        if key.lower() == 'done':
            break

        assignment = input("  Assignment: ")
        target = input("  Target: ")

        assignments.append({
            'key': key,
            'assignment': assignment,
            'target': target
        })

    if not assignments:
        print()
        print("Nessun assignment inserito.")
        print("Se Generic Keyboard non esiste o e' vuoto = OK!")
        return [], []

    # Identify conflicts
    print()
    print("="*70)
    print("POSSIBILI CONFLITTI CON MIDI")
    print("="*70)

    midi_functions = [
        'Browser.Tree.Scroll',
        'Browser.Tree.Select',
        'Browser.List',
        'Crossfader',
        'Volume',
        'Load',
        'Play',
        'Position',
    ]

    conflicts = []
    for a in assignments:
        for mf in midi_functions:
            if mf.lower() in a['assignment'].lower():
                conflicts.append(a)
                print(f"\nOVERLAP:")
                print(f"   Keyboard: {a['key']} -> {a['assignment']}")
                print(f"   MIDI: Stesso assignment disponibile")
                print(f"   -> Possibile doppio trigger")

    if not conflicts:
        print("\nOK: Nessun overlap evidente")

    return assignments, conflicts

if __name__ == "__main__":
    print()
    assignments, conflicts = analyze_keyboard_conflicts()

    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total keyboard assignments: {len(assignments)}")
    print(f"Conflitti con MIDI: {len(conflicts)}")
    print()

    if conflicts:
        print("RACCOMANDAZIONE:")
        print("Disabilita 'Generic Keyboard' per test MIDI puri")
        print()
        print("COME:")
        print("  1. Traktor > Preferences > Controller Manager")
        print("  2. Seleziona 'Generic Keyboard'")
        print("  3. Uncheck 'Device is active'")
        print("  4. Apply > OK")
        print("  5. Rilancia i test MIDI")
    else:
        print("Generic Keyboard non sembra essere il problema.")
        print("Il conflitto potrebbe essere:")
        print("  - Timing tra comandi MIDI")
        print("  - Bug in Traktor stesso")
        print("  - Controller hardware fisico collegato")
