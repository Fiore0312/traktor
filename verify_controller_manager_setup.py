#!/usr/bin/env python3
"""
Guida interattiva per verificare setup Controller Manager.
Identifica conflitti tra Generic MIDI e Generic Keyboard.
"""

def verify_traktor_setup():
    """Checklist setup Traktor."""

    print("="*70)
    print("VERIFICA TRAKTOR CONTROLLER MANAGER SETUP")
    print("="*70)
    print()
    print("Apri Traktor > Preferences (Gear icon) > Controller Manager")
    print()

    # Check 1: Device List
    print("CHECK 1: DEVICE LIST")
    print("-"*70)
    print("Nella colonna sinistra, quanti device vedi?")
    print()
    print("  a) Solo 'Generic MIDI' (1 device)")
    print("  b) 'Generic MIDI' + 'Generic Keyboard' (2 devices)")
    print("  c) Altro")
    print()
    device_count = input("Risposta (a/b/c): ").lower()

    if device_count == 'b':
        print()
        print("WARNING: Hai ENTRAMBI attivi!")
        print("   Questo puo' causare conflitti.")
        print()
        print("AZIONE SUGGERITA:")
        print("   1. Seleziona 'Generic Keyboard'")
        print("   2. Guarda i suoi assignment")
        print("   3. Verifica se ci sono overlap con MIDI")
        print()
        input("Premi ENTER dopo aver controllato...")

        print()
        print("DOMANDA: Generic Keyboard ha assegnamenti per:")
        print("  - Browser navigation? (y/n)")
        kb_browser = input("  ").lower() == 'y'
        print("  - Crossfader? (y/n)")
        kb_crossfader = input("  ").lower() == 'y'

        if kb_browser or kb_crossfader:
            print()
            print("CONFLITTO TROVATO!")
            print("   Generic Keyboard interferisce con Generic MIDI")
            print()
            print("SOLUZIONE:")
            print("   OPZIONE A (Raccomandato): Disabilita Generic Keyboard")
            print("     - Click su 'Generic Keyboard'")
            print("     - Uncheck 'Device is active'")
            print("     - Apply > OK")
            print()
            print("   OPZIONE B: Rimuovi assignment specifici")
            print("     - Elimina solo Browser/Crossfader da Keyboard")
            print("     - Lascia attivi altri shortcuts non in conflitto")
            return False

    # Check 2: MIDI Device Assignments
    print()
    print("CHECK 2: GENERIC MIDI ASSIGNMENTS")
    print("-"*70)
    print("Seleziona 'Generic MIDI' nella lista")
    print()
    print("Nella tabella Assignment, cerca:")
    print("  1. Browser Tree Scroll/Navigate")
    print("  2. Crossfader")
    print()
    print("Quale CC number vedi per ciascuno?")
    print()
    browser_cc = input("Browser CC number (es. 72): ")
    crossfader_cc = input("Crossfader CC number (es. 56): ")

    if browser_cc == crossfader_cc:
        print()
        print("CONFLITTO CONFERMATO NEL MIDI!")
        print(f"   Entrambi usano CC {browser_cc}")
        return False
    else:
        print()
        print("OK: CC numbers diversi")
        print(f"   Browser: CC {browser_cc}")
        print(f"   Crossfader: CC {crossfader_cc}")

    # Check 3: In-Port
    print()
    print("CHECK 3: MIDI INPUT PORT")
    print("-"*70)
    print("In alto, quale 'In-Port' e' selezionato per Generic MIDI?")
    print()
    in_port = input("Nome porta (es. 'Traktor MIDI Bus 1'): ")

    if "traktor" not in in_port.lower() and "loopmidi" not in in_port.lower():
        print()
        print("WARNING: Porta inaspettata!")
        print(f"   Visto: {in_port}")
        print("   Atteso: 'Traktor MIDI Bus 1' (loopMIDI)")
    else:
        print(f"   OK: Porta corretta: {in_port}")

    return True

if __name__ == "__main__":
    print()
    result = verify_traktor_setup()
    print()
    print("="*70)
    if result:
        print("SETUP SEMBRA CORRETTO")
        print("   Il problema potrebbe essere altrove")
    else:
        print("PROBLEMI TROVATI")
        print("   Segui le azioni suggerite sopra")
    print("="*70)
