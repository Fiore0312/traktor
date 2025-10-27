"""
Test e Fix Volume Control
Testa i comandi MIDI per il volume dei deck
"""

import time
from traktor_midi_driver import TraktorMIDIDriver

def test_volume_control():
    """Test volume control per entrambi i deck"""

    print("="*70)
    print("TEST VOLUME CONTROL")
    print("="*70)

    midi = TraktorMIDIDriver()

    # Test 1: Deck A volume a zero
    print("\n1️⃣ TEST: Deck A volume → 0")
    print("   Inviando CC 65, valore 0...")
    midi.send_cc(65, 0)
    time.sleep(0.5)
    print("   ✅ Comando inviato")
    input("   👀 VERIFICA in Traktor: il fader Deck A è a ZERO? (Enter per continuare)")

    # Test 2: Deck A volume a 85%
    print("\n2️⃣ TEST: Deck A volume → 85%")
    target_value = int(127 * 0.85)  # 108
    print(f"   Inviando CC 65, valore {target_value}...")
    midi.send_cc(65, target_value)
    time.sleep(0.5)
    print("   ✅ Comando inviato")
    input("   👀 VERIFICA in Traktor: il fader Deck A è a ~85%? (Enter per continuare)")

    # Test 3: Deck B volume a zero
    print("\n3️⃣ TEST: Deck B volume → 0")
    print("   Inviando CC 60, valore 0...")
    midi.send_cc(60, 0)
    time.sleep(0.5)
    print("   ✅ Comando inviato")
    input("   👀 VERIFICA in Traktor: il fader Deck B è a ZERO? (Enter per continuare)")

    # Test 4: Deck B volume a 85%
    print("\n4️⃣ TEST: Deck B volume → 85%")
    target_value = int(127 * 0.85)  # 108
    print(f"   Inviando CC 60, valore {target_value}...")
    midi.send_cc(60, target_value)
    time.sleep(0.5)
    print("   ✅ Comando inviato")
    input("   👀 VERIFICA in Traktor: il fader Deck B è a ~85%? (Enter per continuare)")

    # Test 5: RAPID fire - volume 0 con delay
    print("\n5️⃣ TEST: RAPID FIRE - Entrambi deck a 0 (con delay)")
    print("   Deck A volume → 0...")
    midi.send_cc(65, 0)
    time.sleep(0.2)  # Delay tra comandi
    print("   Deck B volume → 0...")
    midi.send_cc(60, 0)
    time.sleep(0.5)
    print("   ✅ Comandi inviati")
    input("   👀 VERIFICA in Traktor: ENTRAMBI i fader sono a ZERO? (Enter per continuare)")

    # Test 6: IMMEDIATE fire - senza delay
    print("\n6️⃣ TEST: IMMEDIATE FIRE - Entrambi deck a 85% (NO delay)")
    target = int(127 * 0.85)
    print(f"   Deck A volume → {target}...")
    midi.send_cc(65, target)
    print(f"   Deck B volume → {target}... (immediatamente)")
    midi.send_cc(60, target)
    time.sleep(0.5)
    print("   ✅ Comandi inviati")
    input("   👀 VERIFICA in Traktor: ENTRAMBI i fader sono a ~85%? (Enter per continuare)")

    print("\n" + "="*70)
    print("TEST COMPLETATO")
    print("="*70)

    # Chiedi risultati
    print("\n📊 RISULTATI:")
    print("\nQuali test hanno FUNZIONATO? (scrivi numeri separati da virgola, es: 1,2,3)")
    working = input("Test funzionanti: ")

    print("\nQuali test NON hanno funzionato? (scrivi numeri separati da virgola)")
    failing = input("Test falliti: ")

    print("\n" + "="*70)
    print("DIAGNOSI")
    print("="*70)

    if '1' in failing or '3' in failing:
        print("\n❌ PROBLEMA: Volume a 0 NON funziona")
        print("\n🔧 POSSIBILI CAUSE:")
        print("   1. Il fader in Traktor non è mappato a CC 65/60")
        print("   2. Il fader è in modalità RELATIVE invece di ABSOLUTE")
        print("   3. MIDI Interaction Mode è DIRECT invece di GENERIC MIDI")
        print("\n💡 SOLUZIONE:")
        print("   1. Apri Traktor → Preferences → Controller Manager")
        print("   2. Trova il mapping per 'Deck A Volume' e 'Deck B Volume'")
        print("   3. Verifica che siano mappati a CC 65 e CC 60")
        print("   4. Verifica che il tipo sia 'Fader' o 'Absolute'")
        print("   5. Se il problema persiste, prova a ricreare il mapping")

    if '5' in failing:
        print("\n❌ PROBLEMA: Comandi rapidi con delay NON funzionano")
        print("\n🔧 CAUSA PROBABILE:")
        print("   Traktor richiede delay maggiore tra comandi MIDI consecutivi")
        print("\n💡 SOLUZIONE:")
        print("   Aumentare delay a 0.5s o 1.0s tra comandi")

    if '6' in failing:
        print("\n❌ PROBLEMA: Comandi IMMEDIATI (senza delay) NON funzionano")
        print("\n🔧 CAUSA PROBABILE:")
        print("   Traktor perde comandi MIDI quando arrivano troppo velocemente")
        print("\n💡 SOLUZIONE:")
        print("   SEMPRE aggiungere delay 0.2-0.5s tra comandi MIDI")

    if failing.strip() == '':
        print("\n✅ TUTTI I TEST FUNZIONANO!")
        print("\n💡 Il problema è probabilmente nel codice del safety check")
        print("   Verifica che il metodo set_volume() usi i CC corretti")

    print("\n" + "="*70)

if __name__ == "__main__":
    test_volume_control()
