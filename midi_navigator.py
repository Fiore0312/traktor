"""Navigazione MIDI nel browser Traktor"""

import mido
import time

class TraktorNavigator:
    def __init__(self, midi_port='Traktor MIDI Bus 1'):
        try:
            self.port = mido.open_output(midi_port)
            self.current_position = 0
            print(f"MIDI connected to: {midi_port}")
        except Exception as e:
            print(f"WARNING: Could not open MIDI port '{midi_port}': {e}")
            print("Running in DRY-RUN mode (no MIDI commands will be sent)")
            self.port = None
            self.current_position = 0
    
    def navigate_to(self, target_position, delay=0.05):
        """Naviga alla posizione target"""
        distance = target_position - self.current_position
        
        if distance == 0:
            print(f"Already at position {target_position}")
            return
        
        print(f"Navigating from {self.current_position} to {target_position} ({distance} steps)")
        
        # CC #1 per scroll
        direction = 127 if distance > 0 else 1
        
        for _ in range(abs(distance)):
            if self.port:
                self.port.send(mido.Message('control_change',
                                           channel=0,
                                           control=1,
                                           value=direction))
                time.sleep(delay)  # Small delay between commands
        
        self.current_position = target_position
        print(f"  -> Navigated to position {target_position}")
    
    def load_to_deck(self, deck_letter):
        """Load su deck A/B/C/D"""
        deck_map = {'A': 43, 'B': 44, 'C': 45, 'D': 46}
        deck_letter_upper = deck_letter.upper()
        cc_num = deck_map.get(deck_letter_upper)
        
        if not cc_num:
            print(f"ERROR: Invalid deck '{deck_letter}'. Must be A, B, C, or D")
            return False
        
        if self.port:
            self.port.send(mido.Message('control_change',
                                       channel=0,
                                       control=cc_num,
                                       value=127))
            print(f"Loaded track to Deck {deck_letter_upper}")
            return True
        else:
            print(f"DRY-RUN: Would load to Deck {deck_letter_upper} (CC #{cc_num})")
            return False
    
    def close(self):
        """Close MIDI port"""
        if self.port:
            self.port.close()
            print("MIDI port closed")

if __name__ == '__main__':
    # Test
    nav = TraktorNavigator()
    print("\nTest navigation:")
    nav.navigate_to(5)
    nav.navigate_to(10)
    nav.load_to_deck('B')
    nav.close()
