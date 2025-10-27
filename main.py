"""Script principale - Demo completo"""

from collection_parser import parse_collection
from camelot_matcher import find_compatible_tracks
from midi_navigator import TraktorNavigator
import sqlite3

def main():
    print("=" * 60)
    print("AUTONOMOUS DJ - INTELLIGENT TRACK SELECTION")
    print("=" * 60)
    
    # 1. Parse collection (fai UNA volta, poi commenta)
    print("\n[1/4] Parsing collection.nml...")
    print("      (This may take a minute...)")
    try:
        count = parse_collection(r'C:\Users\Utente\Documents\Native Instruments\Traktor 3.11.1\collection.nml')
        print(f"      -> Parsed {count} tracks")
    except Exception as e:
        print(f"      ERROR: {e}")
        print("      Trying to use existing database...")
    
    # 2. Get current track info (esempio: track su Deck A)
    print("\n[2/4] Current track info:")
    current_track = {
        'bpm': 128.0,
        'camelot': '8A',
        'name': 'Example Track'
    }
    print(f"      BPM: {current_track['bpm']}")
    print(f"      Key: {current_track['camelot']}")
    
    # 3. Trova traccia compatibile
    print("\n[3/4] Finding compatible tracks...")
    compatible = find_compatible_tracks(
        current_track['bpm'],
        current_track['camelot']
    )
    
    if not compatible:
        print("      No compatible tracks found!")
        print("      Tip: Make sure your tracks have BPM and Key analyzed in Traktor")
        return
    
    # Show options
    print(f"      Found {len(compatible)} compatible tracks:")
    for i, track in enumerate(compatible[:3], 1):
        print(f"      {i}. {track[2]} @ {track[3]} BPM, {track[5]}")
    
    # Select first one
    next_track = compatible[0]
    print(f"\n      Selected: {next_track[2]}")
    print(f"      BPM: {next_track[3]}, Key: {next_track[5]}")
    print(f"      Position in collection: {next_track[7]}")
    
    # 4. Navigate e load
    print("\n[4/4] Loading track to Deck B...")
    nav = TraktorNavigator()
    
    try:
        # Navigate to position
        nav.navigate_to(next_track[7])
        
        # Load to Deck B
        nav.load_to_deck('B')
        
        print("\n" + "=" * 60)
        print("SUCCESS! Track loaded to Deck B")
        print("=" * 60)
        
    except Exception as e:
        print(f"ERROR during MIDI navigation: {e}")
    finally:
        nav.close()

if __name__ == '__main__':
    main()
