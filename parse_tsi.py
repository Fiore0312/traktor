#!/usr/bin/env python3
"""
Parse Traktor TSI file to extract MIDI CC mappings.
TSI files are XML-based but may contain binary encoding.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
import re


def parse_tsi_file(tsi_path):
    """
    Parse TSI file and extract MIDI CC mappings.

    Returns:
        dict: Mapping of CC numbers to their functions
    """
    print(f"[PARSE] Analyzing: {tsi_path}")

    mappings = []

    try:
        # Try to parse as XML
        tree = ET.parse(tsi_path)
        root = tree.getroot()

        print(f"[OK] XML root tag: {root.tag}")
        print(f"[OK] XML root attributes: {root.attrib}")

        # Explore structure
        print("\n[STRUCTURE] Top-level elements:")
        for child in root:
            print(f"  - {child.tag} (attrib: {child.attrib})")

        # Look for MIDI-related elements
        print("\n[SEARCH] Looking for MIDI assignments...")

        # Search for common TSI patterns
        midi_elements = root.findall(".//Entry")
        print(f"[INFO] Found {len(midi_elements)} Entry elements")

        # Extract mappings
        for entry in midi_elements:
            mapping = {}

            # Look for MIDI note/CC
            midi_note = entry.find(".//MidiNote")
            if midi_note is not None:
                mapping['cc'] = midi_note.text

            # Look for assignment/target
            assignment = entry.find(".//Assignment")
            if assignment is not None:
                mapping['function'] = assignment.text

            # Look for target (deck, etc)
            target = entry.find(".//Target")
            if target is not None:
                mapping['target'] = target.text

            if mapping:
                mappings.append(mapping)

        return mappings

    except ET.ParseError as e:
        print(f"[WARN] XML parse error: {e}")
        print("[INFO] TSI may contain binary data, trying alternative approach...")

        # Alternative: Read as binary and extract strings
        return parse_tsi_binary(tsi_path)


def parse_tsi_binary(tsi_path):
    """
    Parse TSI as binary file and extract readable strings.
    """
    print("[BINARY] Reading TSI as binary...")

    with open(tsi_path, 'rb') as f:
        content = f.read()

    # Convert to string, ignoring errors
    text = content.decode('utf-8', errors='ignore')

    # Look for patterns
    patterns = {
        'midi_note': r'MidiNote.*?(\d+)',
        'assignment': r'Assignment.*?([A-Za-z_]+)',
        'target': r'Target.*?(Deck[AB]|Browser)',
    }

    mappings = []

    # Extract all readable text chunks
    lines = text.split('\x00')  # Split on null bytes

    midi_keywords = ['Load', 'Play', 'Cue', 'Sync', 'Browser', 'DeckA', 'DeckB',
                     'Volume', 'EQ', 'Loop', 'Master', 'Tempo']

    print(f"[BINARY] Extracted {len(lines)} text chunks")

    relevant_lines = []
    for line in lines:
        if any(keyword.lower() in line.lower() for keyword in midi_keywords):
            relevant_lines.append(line.strip())

    print(f"[BINARY] Found {len(relevant_lines)} relevant lines")

    return relevant_lines


def print_mappings_table(mappings):
    """Print mappings in structured format."""
    print("\n" + "=" * 80)
    print("MIDI CC MAPPINGS FROM TSI")
    print("=" * 80)

    if isinstance(mappings, list) and mappings and isinstance(mappings[0], dict):
        # Dict format
        print(f"{'CC':<6} | {'Function':<30} | {'Target':<20}")
        print("-" * 80)
        for m in mappings:
            cc = m.get('cc', 'N/A')
            func = m.get('function', 'N/A')
            target = m.get('target', 'N/A')
            print(f"{cc:<6} | {func:<30} | {target:<20}")
    else:
        # String format
        print("\nRelevant text chunks:")
        for i, line in enumerate(mappings[:50], 1):  # First 50 lines
            if line:
                print(f"{i:3}. {line}")


def compare_with_python_driver():
    """
    Compare TSI mappings with Python driver.
    """
    print("\n" + "=" * 80)
    print("PYTHON DRIVER CC USAGE")
    print("=" * 80)

    driver_path = Path("C:/traktor/traktor_midi_driver.py")

    with open(driver_path, 'r') as f:
        content = f.read()

    # Extract CC definitions from TraktorCC enum
    cc_pattern = r'([A-Z_]+)\s*=\s*(\d+)'
    matches = re.findall(cc_pattern, content)

    print(f"{'CC Value':<10} | {'Python Constant':<40}")
    print("-" * 80)

    cc_dict = {}
    for name, value in matches:
        cc_dict[int(value)] = name
        print(f"{value:<10} | {name:<40}")

    print(f"\n[INFO] Total CC definitions in Python: {len(cc_dict)}")

    return cc_dict


def main():
    """Main entry point."""
    tsi_path = Path("C:/traktor/mappature_20_10.tsi")

    if not tsi_path.exists():
        print(f"[ERROR] TSI file not found: {tsi_path}")
        return

    print("=" * 80)
    print("TSI MAPPING ANALYZER")
    print("=" * 80)
    print()

    # Parse TSI
    mappings = parse_tsi_file(tsi_path)

    # Print results
    if mappings:
        print_mappings_table(mappings)

    # Compare with Python
    print("\n")
    python_ccs = compare_with_python_driver()

    # Next steps
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review mappings above")
    print("2. Identify CC mismatches between TSI and Python")
    print("3. Update traktor_midi_driver.py with correct values")
    print("4. Create validation script")


if __name__ == "__main__":
    main()
