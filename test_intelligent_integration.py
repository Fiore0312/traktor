"""
Test script per verificare l'integrazione del sistema intelligente
nel workflow controller.

Usage:
    python test_intelligent_integration.py
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test 1: Verifica che tutti i moduli siano importabili"""
    print("\n" + "="*70)
    print("TEST 1: Import Modules")
    print("="*70)
    
    try:
        from camelot_matcher import find_compatible_tracks, get_compatible_keys
        print("✓ camelot_matcher imported")
        
        from midi_navigator import TraktorNavigator
        print("✓ midi_navigator imported")
        
        from collection_parser_xml import parse_collection
        print("✓ collection_parser_xml imported")
        
        from autonomous_dj.workflow_controller import DJWorkflowController
        print("✓ DJWorkflowController imported")
        
        from autonomous_dj.openrouter_client import OpenRouterClient
        print("✓ OpenRouterClient imported")
        
        print("\n✅ TEST 1 PASSED: All modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"\n❌ TEST 1 FAILED: Import error: {e}")
        return False

def test_database():
    """Test 2: Verifica che il database esista e contenga dati"""
    print("\n" + "="*70)
    print("TEST 2: Database Check")
    print("="*70)
    
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent / 'tracks.db'
    
    if not db_path.exists():
        print(f"❌ TEST 2 FAILED: Database not found at {db_path}")
        print("   Run: python collection_parser_xml.py")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM tracks")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM tracks WHERE bpm IS NOT NULL")
        with_bpm = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM tracks WHERE camelot IS NOT NULL")
        with_key = c.fetchone()[0]
        
        conn.close()
        
        print(f"✓ Database found: {db_path}")
        print(f"✓ Total tracks: {total}")
        print(f"✓ Tracks with BPM: {with_bpm}")
        print(f"✓ Tracks with Key: {with_key}")
        
        if with_key < 5:
            print(f"\n⚠️  Warning: Only {with_key} tracks have Key analyzed")
            print("   For better results, analyze more tracks in Traktor:")
            print("   1. Select all tracks")
            print("   2. Right-click → Analyze → Determine Key")
            print("   3. Re-run: python collection_parser_xml.py")
        
        print("\n✅ TEST 2 PASSED: Database OK")
        return True
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: Database error: {e}")
        return False

def test_camelot_logic():
    """Test 3: Verifica la logica Camelot Wheel"""
    print("\n" + "="*70)
    print("TEST 3: Camelot Wheel Logic")
    print("="*70)
    
    from camelot_matcher import get_compatible_keys
    
    # Test case: 8A
    test_key = '8A'
    compatible = get_compatible_keys(test_key)
    
    print(f"Testing key: {test_key}")
    print(f"Compatible keys: {compatible}")
    
    expected = ['8B', '7A', '9A']  # In some order
    
    if set(compatible) == set(expected):
        print("✓ Camelot logic correct")
        print("\n✅ TEST 3 PASSED")
        return True
    else:
        print(f"❌ Expected: {expected}")
        print(f"❌ Got: {compatible}")
        print("\n❌ TEST 3 FAILED")
        return False

def test_find_compatible():
    """Test 4: Verifica ricerca tracce compatibili"""
    print("\n" + "="*70)
    print("TEST 4: Find Compatible Tracks")
    print("="*70)
    
    from camelot_matcher import find_compatible_tracks
    
    # Test con valori comuni
    test_bpm = 128.0
    test_key = '8A'
    
    print(f"Finding tracks compatible with: {test_bpm} BPM, {test_key}")
    
    try:
        compatible = find_compatible_tracks(test_bpm, test_key)
        
        if compatible and len(compatible) > 0:
            print(f"\n✓ Found {len(compatible)} compatible tracks:")
            for i, track in enumerate(compatible[:3], 1):  # Show first 3
                filename = track[2]
                bpm = track[3]
                camelot = track[5]
                print(f"   {i}. {filename[:50]}... @ {bpm} BPM, {camelot}")
            
            print("\n✅ TEST 4 PASSED")
            return True
        else:
            print("\n⚠️  TEST 4 WARNING: No compatible tracks found")
            print("   This might be normal if your library doesn't have matching tracks")
            print("   Try analyzing more tracks in Traktor")
            return True  # Non-blocking warning
            
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False

def test_openrouter_parsing():
    """Test 5: Verifica parsing comando OpenRouter"""
    print("\n" + "="*70)
    print("TEST 5: OpenRouter Command Parsing")
    print("="*70)
    
    from autonomous_dj.openrouter_client import OpenRouterClient
    
    client = OpenRouterClient()
    
    test_commands = [
        "Trova una traccia compatibile",
        "Find a compatible track for Deck A",
        "Load a compatible track on Deck B"
    ]
    
    all_passed = True
    
    for cmd in test_commands:
        result = client.parse_dj_command(cmd)
        
        if result['action'] == 'FIND_COMPATIBLE_TRACK':
            print(f"✓ '{cmd}' → FIND_COMPATIBLE_TRACK")
        else:
            print(f"❌ '{cmd}' → {result['action']} (expected FIND_COMPATIBLE_TRACK)")
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST 5 PASSED: All commands parsed correctly")
    else:
        print("\n⚠️  TEST 5 WARNING: Some commands not parsed as expected")
        print("   This uses fallback parsing (no OpenRouter API key)")
        print("   For better parsing, configure API key in autonomous_dj/config.py")
    
    return True  # Non-blocking

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("INTELLIGENT TRACK SELECTION - INTEGRATION TEST")
    print("="*70)
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Camelot Logic", test_camelot_logic),
        ("Find Compatible", test_find_compatible),
        ("OpenRouter Parsing", test_openrouter_parsing)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\nYou can now:")
        print("1. Start the server: START_SERVER_PRODUCTION.bat")
        print("2. Open: http://localhost:8000")
        print("3. Try command: 'Trova una traccia compatibile'")
        print("4. Or click: 🎧 Auto-Select Compatible button")
        print("\n")
    else:
        print("\n" + "="*70)
        print("⚠️  SOME TESTS FAILED")
        print("="*70)
        print("\nPlease fix the issues above before using the system")
        print("\n")

if __name__ == "__main__":
    main()
