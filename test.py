"""Test rapido del sistema"""

print("=" * 60)
print("TEST SISTEMA INTELLIGENTE SELEZIONE TRACCE")
print("=" * 60)

# Test 1: Parse collection
print("\nTest 1: Parsing collection.nml...")
try:
    from collection_parser import parse_collection
    count = parse_collection(r'C:\Users\Utente\Documents\Native Instruments\Traktor 3.11.1\collection.nml')
    print(f"[OK] Collection parsed: {count} tracks")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 2: Query database
print("\nTest 2: Querying database...")
try:
    import sqlite3
    conn = sqlite3.connect('tracks.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM tracks")
    count = c.fetchone()[0]
    print(f"[OK] Database has {count} tracks")
    
    # Show sample
    c.execute("SELECT filename, bpm, camelot FROM tracks WHERE bpm IS NOT NULL LIMIT 5")
    samples = c.fetchall()
    print("\n  Sample tracks:")
    for filename, bpm, camelot in samples:
        print(f"    - {filename}: {bpm} BPM, {camelot}")
    
    conn.close()
except Exception as e:
    print(f"[FAIL] {e}")

# Test 3: Camelot logic
print("\nTest 3: Camelot matching logic...")
try:
    from camelot_matcher import get_compatible_keys
    keys = get_compatible_keys('8A')
    print(f"[OK] Compatible keys for 8A: {keys}")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 4: Find compatible tracks
print("\nTest 4: Finding compatible tracks...")
try:
    from camelot_matcher import find_compatible_tracks
    compatible = find_compatible_tracks(128.0, '8A')
    if compatible:
        print(f"[OK] Found {len(compatible)} compatible tracks")
        print(f"  First match: {compatible[0][2]} @ {compatible[0][3]} BPM, {compatible[0][5]}")
    else:
        print("[WARN] No compatible tracks found (might need more tracks with BPM/Key)")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 5: MIDI Navigator
print("\nTest 5: MIDI Navigator...")
try:
    from midi_navigator import TraktorNavigator
    nav = TraktorNavigator()
    print("[OK] MIDI Navigator initialized")
    nav.close()
except Exception as e:
    print(f"[FAIL] {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
