#!/usr/bin/env python3
"""
Verify synchronization between traktor_midi_mapping.json and traktor_midi_driver.py
Reports any mismatches between configuration and code.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
import json
from pathlib import Path
import re
from traktor_midi_driver import TraktorCC


def load_json_config():
    """Load MIDI mapping from JSON."""
    config_path = Path("C:/traktor/config/traktor_midi_mapping.json")

    with open(config_path, 'r') as f:
        config = json.load(f)

    return config


def extract_python_cc():
    """Extract CC mappings from Python TraktorCC enum."""
    cc_map = {}

    for name, value in TraktorCC.__members__.items():
        cc_map[name] = value

    return cc_map


def compare_mappings():
    """Compare JSON config with Python driver."""
    print("=" * 80)
    print("MIDI MAPPING SYNCHRONIZATION CHECK")
    print("=" * 80)
    print()

    # Load both sources
    json_config = load_json_config()
    python_cc = extract_python_cc()

    print(f"[INFO] JSON config last verified: {json_config.get('last_verified')}")
    print(f"[INFO] JSON source: {json_config.get('verified_from')}")
    print(f"[INFO] Python CC definitions: {len(python_cc)}")
    print()

    mismatches = []
    matches = []

    # Check Deck A
    print("=" * 80)
    print("DECK A VERIFICATION")
    print("=" * 80)

    deck_a_mappings = {
        'DECK_A_PLAY_PAUSE': json_config['deck_a']['play_pause'],
        'DECK_A_LOAD_TRACK': json_config['deck_a']['load_track'],
        'DECK_A_CUE': json_config['deck_a']['cue'],
        'DECK_A_SYNC_ON': json_config['deck_a']['sync_on'],
        'DECK_A_TEMPO_MASTER': json_config['deck_a']['tempo_master'],
        'DECK_A_TEMPO': json_config['deck_a']['tempo_adjust'],
        'DECK_A_VOLUME': json_config['deck_a']['volume'],
        'DECK_A_EQ_HIGH': json_config['deck_a']['eq_high'],
        'DECK_A_EQ_MID': json_config['deck_a']['eq_mid'],
        'DECK_A_EQ_LOW': json_config['deck_a']['eq_low'],
        'DECK_A_LOOP_ACTIVE': json_config['deck_a']['loop_active'],
        'DECK_A_LOOP_OUT': json_config['deck_a']['loop_out'],
        'DECK_A_LOOP_IN_SET_CUE': json_config['deck_a']['loop_in_set_cue'],
    }

    for py_name, json_cc in deck_a_mappings.items():
        py_cc = python_cc.get(py_name)

        if py_cc == json_cc:
            print(f"[OK] {py_name:25s} = CC {py_cc:3d} (matches JSON)")
            matches.append(py_name)
        else:
            print(f"[MISMATCH] {py_name:25s}: Python={py_cc:3d}, JSON={json_cc:3d}")
            mismatches.append({
                'constant': py_name,
                'python': py_cc,
                'json': json_cc
            })

    # Check Deck B
    print()
    print("=" * 80)
    print("DECK B VERIFICATION")
    print("=" * 80)

    deck_b_mappings = {
        'DECK_B_PLAY_PAUSE': json_config['deck_b']['play_pause'],
        'DECK_B_LOAD_TRACK': json_config['deck_b']['load_track'],
        'DECK_B_CUE': json_config['deck_b']['cue'],
        'DECK_B_SYNC_ON': json_config['deck_b']['sync_on'],
        'DECK_B_TEMPO_MASTER': json_config['deck_b']['tempo_master'],
        'DECK_B_TEMPO': json_config['deck_b']['tempo_adjust'],
        'DECK_B_VOLUME': json_config['deck_b']['volume'],
        'DECK_B_EQ_HIGH': json_config['deck_b']['eq_high'],
        'DECK_B_EQ_MID': json_config['deck_b']['eq_mid'],
        'DECK_B_EQ_LOW': json_config['deck_b']['eq_low'],
        'DECK_B_LOOP_ACTIVE': json_config['deck_b']['loop_active'],
        'DECK_B_LOOP_OUT': json_config['deck_b']['loop_out'],
        'DECK_B_LOOP_IN_SET_CUE': json_config['deck_b']['loop_in_set_cue'],
    }

    for py_name, json_cc in deck_b_mappings.items():
        py_cc = python_cc.get(py_name)

        if py_cc == json_cc:
            print(f"[OK] {py_name:25s} = CC {py_cc:3d} (matches JSON)")
            matches.append(py_name)
        else:
            print(f"[MISMATCH] {py_name:25s}: Python={py_cc:3d}, JSON={json_cc:3d}")
            mismatches.append({
                'constant': py_name,
                'python': py_cc,
                'json': json_cc
            })

    # Check Browser
    print()
    print("=" * 80)
    print("BROWSER VERIFICATION")
    print("=" * 80)

    browser_mappings = {
        'BROWSER_SCROLL_LIST': json_config['browser']['scroll_list'],
        'BROWSER_SCROLL_TREE_DEC': json_config['browser']['scroll_tree_up'],
        'BROWSER_SCROLL_TREE_INC': json_config['browser']['scroll_tree_down'],
        'BROWSER_EXPAND_COLLAPSE': json_config['browser']['expand_collapse'],
    }

    for py_name, json_cc in browser_mappings.items():
        py_cc = python_cc.get(py_name)

        if py_cc == json_cc:
            print(f"[OK] {py_name:25s} = CC {py_cc:3d} (matches JSON)")
            matches.append(py_name)
        else:
            print(f"[MISMATCH] {py_name:25s}: Python={py_cc:3d}, JSON={json_cc:3d}")
            mismatches.append({
                'constant': py_name,
                'python': py_cc,
                'json': json_cc
            })

    # Check Mixer
    print()
    print("=" * 80)
    print("MIXER VERIFICATION")
    print("=" * 80)

    mixer_mappings = {
        'MASTER_VOLUME': json_config['mixer']['master_volume'],
    }

    for py_name, json_cc in mixer_mappings.items():
        py_cc = python_cc.get(py_name)

        if py_cc == json_cc:
            print(f"[OK] {py_name:25s} = CC {py_cc:3d} (matches JSON)")
            matches.append(py_name)
        else:
            print(f"[MISMATCH] {py_name:25s}: Python={py_cc:3d}, JSON={json_cc:3d}")
            mismatches.append({
                'constant': py_name,
                'python': py_cc,
                'json': json_cc
            })

    # Summary
    print()
    print("=" * 80)
    print("SYNCHRONIZATION SUMMARY")
    print("=" * 80)
    print(f"Mappings checked: {len(matches) + len(mismatches)}")
    print(f"Matches: {len(matches)}")
    print(f"Mismatches: {len(mismatches)}")
    print()

    if mismatches:
        print("[ERROR] SYNCHRONIZATION FAILED!")
        print()
        print("Mismatches found:")
        for mismatch in mismatches:
            print(f"  - {mismatch['constant']:25s}: Python={mismatch['python']:3d}, JSON={mismatch['json']:3d}")

        print()
        print("Action required:")
        print("  1. Determine which source is correct (JSON or Python)")
        print("  2. Update the incorrect source")
        print("  3. Re-run this verification script")

        return False
    else:
        print("[OK] ALL MAPPINGS SYNCHRONIZED!")
        print()
        print("Critical mappings verified:")
        print("  - Deck A/B: Transport, Loading, Sync, Mixer")
        print("  - Browser Navigation")
        print("  - Master Volume")
        print()
        print("The Python driver and JSON config are synchronized.")
        print("Both sources reference: 'command_mapping_ok.tsi screenshots'")
        print()

        return True


def main():
    """Main entry point."""
    try:
        result = compare_mappings()

        if result:
            print("=" * 80)
            print("STATUS: READY FOR PRODUCTION")
            print("=" * 80)
            exit(0)
        else:
            print("=" * 80)
            print("STATUS: NEEDS FIXING")
            print("=" * 80)
            exit(1)

    except Exception as e:
        print()
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
