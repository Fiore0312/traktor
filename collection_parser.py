"""
Legge collection.nml e estrae:
- BPM (già analizzato da Traktor)
- Key (già analizzato da Traktor) 
- Path del file
- Position nell'elenco (index)
"""

from traktor_nml_utils import TraktorCollection
from pathlib import Path
import sqlite3
import os

def convert_to_camelot(traktor_key):
    """
    Traktor key format: numero 0-23
    0=C, 1=Db, 2=D, etc.
    0-11 = Major (B), 12-23 = Minor (A)
    """
    if traktor_key is None or traktor_key == '':
        return None
    
    # Convert to int if string
    try:
        key_num = int(traktor_key)
    except (ValueError, TypeError):
        return None
    
    # Mappa Traktor → Camelot
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
    """Parse collection.nml e crea database"""
    print(f"Parsing {nml_path}...")

    collection = TraktorCollection(path=Path(nml_path))
    
    # Crea database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS tracks
                 (id INTEGER PRIMARY KEY,
                  path TEXT UNIQUE,
                  filename TEXT,
                  bpm REAL,
                  key TEXT,
                  camelot TEXT,
                  genre TEXT,
                  position INTEGER)''')
    
    # Popola database
    track_count = 0
    error_count = 0
    
    for idx, entry in enumerate(collection.nml.collection.entry):
        try:
            # Estrai dati
            location = entry.location
            info = entry.info if hasattr(entry, 'info') else None
            tempo = entry.tempo if hasattr(entry, 'tempo') else None
            musical_key = entry.musical_key if hasattr(entry, 'musical_key') else None
            
            # Get path (handle both file:// URLs and direct paths)
            file_path = location.file if hasattr(location, 'file') else ''
            dir_path = location.dir if hasattr(location, 'dir') else ''
            
            # Clean paths
            if file_path.startswith('file://localhost/'):
                file_path = file_path.replace('file://localhost/', '')
            
            full_path = os.path.join(dir_path, file_path)
            filename = os.path.basename(file_path)
            
            # Get BPM
            bpm = None
            if tempo and hasattr(tempo, 'bpm'):
                try:
                    bpm = float(tempo.bpm)
                except:
                    pass
            
            # Get Key
            key_value = None
            if musical_key and hasattr(musical_key, 'value'):
                key_value = musical_key.value
            
            # Convert to Camelot
            camelot = convert_to_camelot(key_value)
            
            # Get Genre
            genre = info.genre if (info and hasattr(info, 'genre')) else ''
            
            # Insert
            c.execute('''INSERT OR REPLACE INTO tracks VALUES 
                         (NULL, ?, ?, ?, ?, ?, ?, ?)''',
                     (full_path, filename, bpm, key_value, 
                      camelot, genre, idx))
            
            track_count += 1
            
            if track_count % 100 == 0:
                print(f"  Processed {track_count} tracks...")
                
        except Exception as e:
            error_count += 1
            if error_count < 10:
                print(f"  Error processing track {idx}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\nDone! Parsed {track_count} tracks ({error_count} errors)")
    return track_count

if __name__ == '__main__':
    # Test
    nml_path = r'C:\Users\Utente\Documents\Native Instruments\Traktor 3.11.1\collection.nml'
    count = parse_collection(nml_path)
    print(f"Database created with {count} tracks")
