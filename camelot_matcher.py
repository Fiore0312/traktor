"""Logica Camelot Wheel per trovare tracce compatibili"""


class CamelotMatcher:
    """
    Wrapper class for Camelot Wheel matching.
    Provides OOP interface to camelot matching functions.
    """

    def __init__(self):
        pass

    def get_compatible_keys(self, camelot):
        """Get compatible keys for a given Camelot key."""
        return get_compatible_keys(camelot)

    def find_compatible_tracks(self, current_bpm, current_camelot, db_path='tracks.db'):
        """Find compatible tracks from database."""
        return find_compatible_tracks(current_bpm, current_camelot, db_path)


def get_compatible_keys(camelot):
    """Ritorna 4 keys compatibili"""
    if not camelot or len(camelot) < 2:
        return []
    
    num = int(camelot[:-1])
    letter = camelot[-1]
    
    compatible = []
    
    # Regola 1: Stesso numero, cambia lettera
    opposite = 'B' if letter == 'A' else 'A'
    compatible.append(f"{num}{opposite}")
    
    # Regola 2: ±1 numero, stessa lettera
    prev = 12 if num == 1 else num - 1
    next_num = 1 if num == 12 else num + 1
    
    compatible.append(f"{prev}{letter}")
    compatible.append(f"{next_num}{letter}")
    
    return compatible

def find_compatible_tracks(current_bpm, current_camelot, db_path='tracks.db'):
    """Query database per tracce compatibili"""
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # BPM range ±6%
    bpm_min = current_bpm * 0.94
    bpm_max = current_bpm * 1.06
    
    # Keys compatibili
    keys = get_compatible_keys(current_camelot)
    
    # Query
    placeholders = ','.join('?' * len(keys))
    query = f'''
        SELECT * FROM tracks
        WHERE camelot IN ({placeholders})
        AND bpm BETWEEN ? AND ?
        ORDER BY RANDOM()
        LIMIT 5
    '''
    
    c.execute(query, (*keys, bpm_min, bpm_max))
    results = c.fetchall()
    conn.close()
    
    return results


if __name__ == '__main__':
    # Test
    print("Testing Camelot Matcher...")
    keys = get_compatible_keys('8A')
    print(f"Compatible keys for 8A: {keys}")
