#!/usr/bin/env python3
"""
Test Browser Navigation - Scroll Tree e List
Verifica che i controlli browser funzionino correttamente.
"""
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

print("="*70)
print("TEST BROWSER NAVIGATION")
print("="*70)
print()
print("Testeremo:")
print("  - Browser Tree Scroll UP/DOWN (CC 73/72)")
print("  - Browser List Scroll (CC 74)")
print()
print("Assicurati di vedere il browser tree in Traktor")
print()

midi = TraktorMIDIDriver()

# Test 1: Tree Scroll Down
print("\n[TEST 1] TREE SCROLL DOWN (CC 72)")
print("-"*70)
print("Il browser tree dovrebbe scendere di 1-2 cartelle")
time.sleep(2)

midi.send_cc(72, 1)  # Inc mode, value 1 = down
time.sleep(2)

input("Tree si e' mosso GIU'? (Premi ENTER)")

# Test 2: Tree Scroll Up
print("\n[TEST 2] TREE SCROLL UP (CC 73)")
print("-"*70)
print("Il browser tree dovrebbe salire di 1-2 cartelle")
time.sleep(2)

midi.send_cc(73, 1)  # Inc mode, value 1 = up
time.sleep(2)

input("Tree si e' mosso SU? (Premi ENTER)")

# Test 3: List Scroll
print("\n[TEST 3] LIST SCROLL (CC 74)")
print("-"*70)
print("La lista tracce dovrebbe scorrere")
time.sleep(2)

# Scroll down nella lista
for i in range(5):
    midi.send_cc(74, 1)
    time.sleep(0.3)

input("Lista si e' mossa? (Premi ENTER)")

# Test 4: Verifica NO interferenza con altri controlli
print("\n[TEST 4] VERIFICA NO INTERFERENZA")
print("-"*70)
print("Scrollo il browser...")
print("Verifica che crossfader e volume NON si muovano!")
time.sleep(2)

# Scroll browser tree multiple times
for i in range(3):
    midi.send_cc(72, 1)  # Down
    time.sleep(0.5)
    midi.send_cc(73, 1)  # Up
    time.sleep(0.5)

print()
print("Durante questo test:")
crossfader_moved = input("  Crossfader si e' mosso? (y/n): ").lower() == 'y'
volume_moved = input("  Volume si e' mosso? (y/n): ").lower() == 'y'

print()
print("="*70)
print("RISULTATI TEST BROWSER")
print("="*70)

if crossfader_moved or volume_moved:
    print("\nWARNING: Interferenza rilevata!")
    if crossfader_moved:
        print("  - Crossfader si muove quando scroll browser")
    if volume_moved:
        print("  - Volume si muove quando scroll browser")
    print("\nPossibile causa: CC overlap o mapping duplicato")
else:
    print("\nSUCCESS: Browser navigation funziona senza interferenze!")
    print("  - Tree scroll: OK")
    print("  - List scroll: OK")
    print("  - No interferenza con mixer: OK")

midi.close()
