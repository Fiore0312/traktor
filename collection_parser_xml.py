"""
Legge collection.nml usando ElementTree (più robusto)
"""

import xml.etree.ElementTree as ET
import sqlite3
from pathlib import Path
import urllib.parse

def convert_to_camelot(traktor_key):
    """Convert Traktor key (0-23) to Camelot notation"""
    if traktor_key is None or traktor_key == '':
        return None
    
    try:
        key_num = int(traktor_key)
    except (ValueError, TypeError):
        return None
    
    # Traktor → Camelot mapping
    key_map = {
        0: "8B",  1: "3B",  2: "10B", 3: "5B",
        4: "12B", 5: "7B",  6: "2B",  7: "9B",
        8: "4B",  9: "11B", 10: "6B", 11: "1B",
        12: "5A", 13: "12A", 14: "7A",  15: "2A",
        16: "9A", 17: "4A",  18: "11A", 19: "6A",
        20: "1A", 21: "8A",  22: "3A",  23: "10A"
    }
    
    return key_map.get(key_num, "Unknown")

def parse_collection(nml_path, db_path='tracks.db'):
    """Parse collection.nml usando XML ElementTree"""
    print(f"Parsing {nml_path} with ElementTree...")
    
    # Parse XML
    tree = ET.parse(nml_path)
    root = tree.getroot()
    
    # Create database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS tracks
                 (id INTEGER PRIMARY KEY,
                  path TEXT UNIQUE,
                  filename TEXT,
                  bpm REAL,
                  key_value TEXT,
                  camelot TEXT,
                  genre TEXT,
                  position INTEGER)''')
    
    # Find all ENTRY elements in COLLECTION
    collection_elem = root.find('.//COLLECTION')
    if collection_elem is None:
        print("ERROR: No COLLECTION element found")
        return 0
    
    track_count = 0
    error_count = 0
    
    for idx, entry in enumerate(collection_elem.findall('ENTRY')):
        try:
            # Get LOCATION
            location = entry.find('LOCATION')
            if location is None:
                continue
            
            # Get file path
            file_path = location.get('FILE', '')
            dir_path = location.get('DIR', '')
            
            # Decode URL encoding
            if file_path.startswith('/:'):
                file_path = file_path[2:]  # Remove /:
            file_path = urllib.parse.unquote(file_path)
            dir_path = urllib.parse.unquote(dir_path)
            
            full_path = dir_path + file_path
            filename = Path(file_path).name
            
            # Get TEMPO (BPM)
            tempo_elem = entry.find('TEMPO')
            bpm = None
            if tempo_elem is not None:
                bpm_str = tempo_elem.get('BPM')
                if bpm_str:
                    try:
                        bpm = float(bpm_str)
                    except:
                        pass
            
            # Get MUSICAL_KEY
            key_elem = entry.find('MUSICAL_KEY')
            key_value = None
            if key_elem is not None:
                key_value = key_elem.get('VALUE')
            
            # Convert to Camelot
            camelot = convert_to_camelot(key_value)
            
            # Get INFO
            info_elem = entry.find('INFO')
            genre = ''
            if info_elem is not None:
                genre = info_elem.get('GENRE', '')
            
            # Insert into database
            c.execute('''INSERT OR REPLACE INTO tracks VALUES 
                         (NULL, ?, ?, ?, ?, ?, ?, ?)''',
                     (full_path, filename, bpm, key_value, camelot, genre, idx))
            
            track_count += 1
            
            if track_count % 100 == 0:
                print(f"  Processed {track_count} tracks...")
                
        except Exception as e:
            error_count += 1
            if error_count < 5:
                print(f"  Error at entry {idx}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nDone! Parsed {track_count} tracks ({error_count} errors)")
    return track_count

if __name__ == '__main__':
    nml_path = r'C:\Users\Utente\Documents\Native Instruments\Traktor 3.11.1\collection.nml'
    count = parse_collection(nml_path)
    print(f"Database created with {count} tracks")
