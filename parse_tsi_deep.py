#!/usr/bin/env python3
"""
Deep TSI parser - explore entire XML structure to find MIDI mappings.
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict


def explore_xml_tree(element, depth=0, max_depth=10):
    """Recursively explore XML tree."""
    indent = "  " * depth

    if depth > max_depth:
        return

    # Print current element
    tag = element.tag
    text = element.text.strip() if element.text and element.text.strip() else ""
    attrib = element.attrib if element.attrib else ""

    # Check if this looks like MIDI data
    midi_keywords = ['midi', 'note', 'cc', 'control', 'assignment', 'deck',
                     'load', 'play', 'cue', 'sync', 'browser', 'mapping']

    is_interesting = any(kw in tag.lower() or kw in text.lower()
                         for kw in midi_keywords)

    if is_interesting or depth < 3:  # Always show first 3 levels
        marker = "[MIDI]" if is_interesting else ""
        if text:
            print(f"{indent}{marker} <{tag}> {attrib} = '{text[:60]}'")
        else:
            print(f"{indent}{marker} <{tag}> {attrib}")

    # Recurse into children
    for child in element:
        explore_xml_tree(child, depth + 1, max_depth)


def extract_all_mappings(root):
    """Extract all possible MIDI mapping data."""
    print("\n" + "=" * 80)
    print("SEARCHING FOR MIDI MAPPINGS")
    print("=" * 80)

    mappings = []

    # Search for various possible element names
    search_paths = [
        ".//Mapping",
        ".//Assignment",
        ".//MidiBinding",
        ".//ControllerBinding",
        ".//Entry",
        ".//*[@Type='Midi']",
        ".//*[@Type='Controller']",
    ]

    for path in search_paths:
        elements = root.findall(path)
        if elements:
            print(f"\n[FOUND] {len(elements)} elements matching: {path}")

            for i, elem in enumerate(elements[:5]):  # Show first 5
                print(f"\n  Element {i+1}:")
                print(f"    Tag: {elem.tag}")
                print(f"    Attrib: {elem.attrib}")

                # Show all children
                for child in elem:
                    child_text = child.text.strip() if child.text else ""
                    print(f"      - {child.tag}: {child_text[:80]}")

                    # Check sub-children
                    for subchild in child:
                        subtext = subchild.text.strip() if subchild.text else ""
                        if subtext:
                            print(f"          - {subchild.tag}: {subtext[:80]}")

    # Also search for numeric values that could be CC numbers (0-127)
    print("\n" + "=" * 80)
    print("SEARCHING FOR NUMERIC VALUES (potential CC numbers)")
    print("=" * 80)

    all_text_elements = root.iter()
    numeric_elements = []

    for elem in all_text_elements:
        if elem.text and elem.text.strip().isdigit():
            value = int(elem.text.strip())
            if 0 <= value <= 127:  # Valid CC range
                numeric_elements.append({
                    'tag': elem.tag,
                    'value': value,
                    'parent': elem.getparent().tag if hasattr(elem, 'getparent') else 'unknown'
                })

    print(f"[INFO] Found {len(numeric_elements)} numeric values in CC range")

    # Group by value
    by_value = defaultdict(list)
    for ne in numeric_elements:
        by_value[ne['value']].append(ne['tag'])

    print("\nValues that appear multiple times (likely important):")
    for value in sorted(by_value.keys()):
        if len(by_value[value]) > 2:  # Appears more than twice
            print(f"  CC {value:3d}: appears in {len(by_value[value])} places")


def main():
    """Main entry point."""
    tsi_path = Path("C:/traktor/mappature_20_10.tsi")

    print("=" * 80)
    print("DEEP TSI STRUCTURE ANALYSIS")
    print("=" * 80)

    tree = ET.parse(tsi_path)
    root = tree.getroot()

    print(f"\n[ROOT] {root.tag}")
    print(f"[ATTRIB] {root.attrib}")
    print(f"[CHILDREN] {len(list(root))} direct children\n")

    # Explore tree
    print("=" * 80)
    print("XML TREE STRUCTURE (first 10 levels)")
    print("=" * 80)
    explore_xml_tree(root, max_depth=10)

    # Extract mappings
    extract_all_mappings(root)


if __name__ == "__main__":
    main()
