#!/usr/bin/env python3
"""
Extract MIDI CC mappings from Traktor TSI file.
Focuses on MIDI-specific assignments (not hardware controllers).
"""
import xml.etree.ElementTree as ET
from pathlib import Path
import base64
import re


def decode_base64_value(value_str):
    """Decode base64-encoded TSI value field."""
    try:
        decoded = base64.b64decode(value_str)
        # Try to extract readable strings
        text = decoded.decode('utf-8', errors='ignore')
        return text
    except:
        return None


def parse_tsi_entries(root):
    """Parse all Entry elements in TSI."""
    entries = root.findall(".//Entry")

    print(f"[INFO] Found {len(entries)} Entry elements")

    midi_related = []

    for entry in entries:
        name = entry.get('Name', '')
        entry_type = entry.get('Type', '')
        value = entry.get('Value', '')

        # Look for MIDI-related entries
        if 'midi' in name.lower() or 'controller' in name.lower():
            print(f"\n[MIDI ENTRY] Name: {name}")
            print(f"             Type: {entry_type}")

            if value and entry_type == '3':  # Type 3 seems to be binary data
                # Try to decode
                decoded = decode_base64_value(value)
                if decoded:
                    # Look for relevant patterns
                    patterns = ['deck', 'play', 'cue', 'load', 'sync', 'browser',
                               'volume', 'eq', 'loop', 'tempo', 'master']

                    if any(p in decoded.lower() for p in patterns):
                        print(f"             Decoded contains: {[p for p in patterns if p in decoded.lower()]}")
                        midi_related.append({
                            'name': name,
                            'type': entry_type,
                            'decoded': decoded[:500]  # First 500 chars
                        })

    return midi_related


def find_mapping_section(root):
    """Find the actual MIDI mapping data section."""
    print("\n" + "=" * 80)
    print("SEARCHING FOR MIDI MAPPING DATA")
    print("=" * 80)

    # Strategy: Look for TraktorSettings entries that contain mapping info
    traktor_settings = root.find(".//TraktorSettings")

    if traktor_settings is None:
        print("[ERROR] No TraktorSettings found!")
        return

    print(f"[OK] Found TraktorSettings element")

    # Iterate through all entries
    for i, entry in enumerate(traktor_settings.findall("Entry")):
        name = entry.get('Name', '')

        # Look for specific mapping entries
        if 'mapping' in name.lower() or 'midi' in name.lower():
            print(f"\n[{i}] Entry Name: {name}")
            print(f"    Type: {entry.get('Type')}")
            value = entry.get('Value', '')

            if value:
                # Try decode
                try:
                    decoded = base64.b64decode(value)
                    text = decoded.decode('utf-8', errors='ignore')

                    # Look for CC numbers (pattern: number between 0-127)
                    cc_numbers = re.findall(r'\b([0-9]{1,3})\b', text)
                    cc_numbers = [int(n) for n in cc_numbers if 0 <= int(n) <= 127]

                    if cc_numbers:
                        print(f"    Potential CC numbers: {cc_numbers[:20]}")

                    # Look for function names
                    functions = re.findall(r'(deck|play|cue|load|sync|browser|volume|eq|loop)',
                                          text, re.IGNORECASE)
                    if functions:
                        print(f"    Functions mentioned: {set(functions)}")

                except Exception as e:
                    print(f"    Decode failed: {e}")


def analyze_python_driver():
    """Extract current Python driver CC mappings."""
    print("\n" + "=" * 80)
    print("PYTHON DRIVER ANALYSIS")
    print("=" * 80)

    driver_path = Path("C:/traktor/traktor_midi_driver.py")

    with open(driver_path, 'r') as f:
        lines = f.readlines()

    # Find TraktorCC enum section
    in_enum = False
    cc_mappings = {}

    for line in lines:
        if 'class TraktorCC' in line:
            in_enum = True
            continue

        if in_enum:
            if line.strip().startswith('class ') or line.strip().startswith('def '):
                break  # End of enum

            # Extract CC definition: NAME = NUMBER
            match = re.match(r'\s+([A-Z_]+)\s*=\s*(\d+)', line)
            if match:
                name = match.group(1)
                value = int(match.group(2))

                # Skip duplicates and non-CC values
                if 'CHANNEL' not in name and 'CONTROL_CHANGE' not in name:
                    if value not in cc_mappings:
                        cc_mappings[value] = []
                    cc_mappings[value].append(name)

    # Print organized
    print(f"\n[INFO] Found {len(cc_mappings)} unique CC numbers in Python\n")

    # Group by function
    transport = []
    loading = []
    mixer = []
    browser = []
    effects = []
    loops = []

    for cc, names in sorted(cc_mappings.items()):
        for name in names:
            if 'PLAY' in name or 'CUE' in name or 'SYNC' in name:
                transport.append(f"  CC {cc:3d}: {name}")
            elif 'LOAD' in name:
                loading.append(f"  CC {cc:3d}: {name}")
            elif 'VOLUME' in name or 'EQ' in name:
                mixer.append(f"  CC {cc:3d}: {name}")
            elif 'BROWSER' in name:
                browser.append(f"  CC {cc:3d}: {name}")
            elif 'FX' in name:
                effects.append(f"  CC {cc:3d}: {name}")
            elif 'LOOP' in name:
                loops.append(f"  CC {cc:3d}: {name}")

    if transport:
        print("[TRANSPORT]")
        for line in transport: print(line)

    if loading:
        print("\n[LOADING]")
        for line in loading: print(line)

    if mixer:
        print("\n[MIXER]")
        for line in mixer: print(line)

    if browser:
        print("\n[BROWSER]")
        for line in browser: print(line)

    if loops:
        print("\n[LOOPS]")
        for line in loops: print(line)

    if effects:
        print("\n[EFFECTS]")
        for line in effects[:10]: print(line)
        if len(effects) > 10:
            print(f"  ... and {len(effects) - 10} more FX mappings")

    return cc_mappings


def main():
    """Main entry point."""
    tsi_path = Path("C:/traktor/mappature_20_10.tsi")

    print("=" * 80)
    print("TSI MIDI MAPPING EXTRACTION")
    print("=" * 80)
    print()

    # Parse TSI
    tree = ET.parse(tsi_path)
    root = tree.getroot()

    # Extract MIDI entries
    midi_entries = parse_tsi_entries(root)

    # Find mapping section
    find_mapping_section(root)

    # Analyze Python driver
    python_ccs = analyze_python_driver()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"TSI file analyzed: {tsi_path.name}")
    print(f"Python CC definitions: {len(python_ccs)}")
    print("\nNext: Manual mapping verification needed")
    print("The TSI file appears to contain hardware controller mappings.")
    print("For MIDI CC verification, we need to:")
    print("  1. Check Traktor's MIDI Learn assignments directly")
    print("  2. Or use the TSI with actual MIDI control assignments")
    print("  3. Cross-reference with Traktor documentation")


if __name__ == "__main__":
    main()
