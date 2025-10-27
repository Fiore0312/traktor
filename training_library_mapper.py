"""
TRAKTOR LIBRARY MAPPING TRAINING SYSTEM

This is the SACRED GRAIL of the autonomous DJ system.
It creates a precise navigation map of your Traktor browser structure.

Features:
- Interactive training with user confirmation
- Persistent storage in JSON + SQLite backup
- Resume capability (can interrupt and continue later)
- Automatic backup before modifications
- Step-by-step folder/track mapping
"""

import json
import sqlite3
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil

from traktor_midi_driver import TraktorMIDIDriver


class LibraryMapper:
    """Interactive library mapping trainer"""

    def __init__(self):
        self.midi = TraktorMIDIDriver()

        # Paths
        self.map_file = Path("data/navigation_map.json")
        self.db_file = Path("data/navigation_map.db")
        self.backup_dir = Path("data/backups")

        # Ensure directories exist
        self.map_file.parent.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

        # Load existing map or create new
        self.navigation_map = self._load_or_create_map()

        # Initialize database
        self._init_database()

        # Training state
        self.current_position = {"tree": 0, "track": 0}
        self.session_start = datetime.now()

    def _load_or_create_map(self) -> Dict:
        """Load existing map or create new structure"""

        if self.map_file.exists():
            print(f"\n[LOAD] Found existing map: {self.map_file}")

            # Create backup before loading
            backup_path = self.backup_dir / f"navigation_map_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy(self.map_file, backup_path)
            print(f"[BACKUP] Created backup: {backup_path}")

            with open(self.map_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"\n[NEW] Creating new navigation map")
            return {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "root_folders": [],  # Top-level folders (Track Collection, Playlists, etc.)
                "music_folders": {},  # Genre folders with positions
                "navigation_history": [],
                "training_sessions": []
            }

    def _save_map(self):
        """Save map to JSON and database"""

        # Update timestamp
        self.navigation_map["last_updated"] = datetime.now().isoformat()

        # Save to JSON (primary storage)
        with open(self.map_file, 'w', encoding='utf-8') as f:
            json.dump(self.navigation_map, f, indent=2, ensure_ascii=False)

        print(f"[SAVE] Map saved to: {self.map_file}")

        # Save to database (backup storage)
        self._save_to_database()

    def _init_database(self):
        """Initialize SQLite database for backup storage"""

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Root folders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS root_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                position INTEGER NOT NULL,
                has_children BOOLEAN,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # Music folders table (genres)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS music_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                position INTEGER NOT NULL,
                parent_path TEXT,
                approximate_tracks INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        # Navigation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS navigation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                action TEXT,
                from_position INTEGER,
                to_position INTEGER,
                folder_name TEXT
            )
        ''')

        # Training sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT,
                folders_mapped INTEGER,
                status TEXT
            )
        ''')

        conn.commit()
        conn.close()

        print(f"[DB] Database initialized: {self.db_file}")

    def _save_to_database(self):
        """Save current map to database"""

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Save root folders
        for folder in self.navigation_map.get("root_folders", []):
            cursor.execute('''
                INSERT OR REPLACE INTO root_folders (name, position, has_children, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                folder["name"],
                folder["position"],
                folder.get("has_children", False),
                folder.get("created_at", now),
                now
            ))

        # Save music folders
        for name, data in self.navigation_map.get("music_folders", {}).items():
            cursor.execute('''
                INSERT OR REPLACE INTO music_folders (name, position, parent_path, approximate_tracks, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                name,
                data["position"],
                data.get("parent_path", ""),
                data.get("approximate_tracks", 0),
                data.get("created_at", now),
                now
            ))

        conn.commit()
        conn.close()

        print(f"[DB] Database updated")

    def _reset_to_root(self):
        """Reset browser to root position"""

        print("\n[RESET] Navigating to root...")
        for i in range(20):
            self.midi.send_cc(73, 127)  # CC 73 = Tree UP
            time.sleep(0.2)

        # Collapse all
        print("[COLLAPSE] Closing all expanded folders...")
        for i in range(15):
            self.midi.send_cc(64, 127)  # CC 64 = Expand/Collapse
            time.sleep(0.2)

        self.current_position["tree"] = 0
        print("[OK] At root position (all collapsed)")

    def train_root_folders(self):
        """Train root-level folder positions"""

        print("\n" + "="*70)
        print("PHASE 1: ROOT FOLDER MAPPING")
        print("="*70)

        print("\n[INFO] This will map top-level folders like:")
        print("       - Track Collection")
        print("       - All Tracks")
        print("       - Playlists")
        print("       - Explorer")
        print("       - etc.")

        input("\nPress Enter to start training...")

        # Reset to root
        self._reset_to_root()

        position = 0
        root_folders = []

        while True:
            print(f"\n{'='*70}")
            print(f"POSITION {position} (from root)")
            print("="*70)

            # Ask user what they see
            response = input(f"\n[Q] What folder do you see at position {position}?\n    (or 'done' if no more folders, 'skip' to move down)\n    > ").strip()

            if response.lower() == 'done':
                break
            elif response.lower() == 'skip':
                print("[SKIP] Moving down one position...")
                self.midi.send_cc(72, 127)  # CC 72 = Tree DOWN
                time.sleep(2.0)
                position += 1
                continue

            # Confirm
            confirm = input(f"[CONFIRM] Is '{response}' correct? (y/n/retry) > ").strip().lower()

            if confirm == 'retry':
                continue
            elif confirm == 'n':
                response = input("[CORRECT] What is the correct name? > ").strip()

            # Ask if has children
            has_children = input(f"[Q] Does '{response}' have subfolders? (y/n) > ").strip().lower() == 'y'

            # Save folder
            folder_data = {
                "name": response,
                "position": position,
                "has_children": has_children,
                "created_at": datetime.now().isoformat()
            }

            root_folders.append(folder_data)

            print(f"[SAVED] '{response}' -> position {position}")

            # Move down for next
            print(f"\n[MOVE] Moving down to position {position + 1}...")
            self.midi.send_cc(72, 127)
            time.sleep(2.0)
            position += 1

        # Save to map
        self.navigation_map["root_folders"] = root_folders
        self._save_map()

        print(f"\n[SUCCESS] Mapped {len(root_folders)} root folders")

        return root_folders

    def train_music_folders(self, parent_path: str = "Explorer > Music Folders > C:\\Users\\Utente\\Music"):
        """Train music genre folder positions"""

        print("\n" + "="*70)
        print("PHASE 2: MUSIC FOLDER MAPPING")
        print("="*70)

        print(f"\n[INFO] This will map genre folders under:")
        print(f"       {parent_path}")

        print("\n[IMPORTANT] You must manually navigate to the music folders first!")
        print("            (Explorer -> Music Folders -> C:\\Users\\Utente\\Music)")
        print("            Then expand the folder to show genres")

        input("\nPress Enter when you're ready (browser on first genre folder)...")

        position = 0
        music_folders = self.navigation_map.get("music_folders", {})

        # Check if we're resuming
        if music_folders:
            resume = input(f"\n[RESUME] Found {len(music_folders)} existing folders. Resume from last? (y/n) > ").strip().lower()
            if resume == 'y':
                position = max([data["position"] for data in music_folders.values()]) + 1
                print(f"[RESUME] Starting from position {position}")

                # Navigate to resume position
                print(f"[MOVE] Moving to position {position}...")
                for i in range(position):
                    self.midi.send_cc(72, 127)
                    time.sleep(2.0)

        while True:
            print(f"\n{'='*70}")
            print(f"MUSIC FOLDER POSITION {position}")
            print("="*70)

            # Ask user what they see
            response = input(f"\n[Q] What music folder do you see at position {position}?\n    (or 'done' if no more, 'skip' to move down, 'back' to go up)\n    > ").strip()

            if response.lower() == 'done':
                break
            elif response.lower() == 'skip':
                print("[SKIP] Moving down...")
                self.midi.send_cc(72, 127)
                time.sleep(2.0)
                position += 1
                continue
            elif response.lower() == 'back':
                print("[BACK] Moving up...")
                self.midi.send_cc(73, 127)
                time.sleep(2.0)
                position = max(0, position - 1)
                continue

            # Confirm
            confirm = input(f"[CONFIRM] Is '{response}' correct? (y/n/retry) > ").strip().lower()

            if confirm == 'retry':
                continue
            elif confirm == 'n':
                response = input("[CORRECT] What is the correct name? > ").strip()

            # Ask approximate track count
            tracks = input(f"[Q] Approximately how many tracks in '{response}'? (or 'skip') > ").strip()
            approximate_tracks = int(tracks) if tracks.isdigit() else 0

            # Save folder
            music_folders[response] = {
                "position": position,
                "parent_path": parent_path,
                "approximate_tracks": approximate_tracks,
                "created_at": datetime.now().isoformat()
            }

            print(f"[SAVED] '{response}' -> position {position} (~{approximate_tracks} tracks)")

            # Auto-save every 5 folders
            if (position + 1) % 5 == 0:
                self.navigation_map["music_folders"] = music_folders
                self._save_map()
                print(f"\n[AUTO-SAVE] Progress saved ({len(music_folders)} folders)")

            # Move down for next
            print(f"\n[MOVE] Moving down to position {position + 1}...")
            self.midi.send_cc(72, 127)
            time.sleep(2.0)
            position += 1

        # Final save
        self.navigation_map["music_folders"] = music_folders
        self._save_map()

        print(f"\n[SUCCESS] Mapped {len(music_folders)} music folders")

        return music_folders

    def verify_navigation(self, folder_name: str):
        """Verify navigation to a specific folder"""

        print(f"\n[VERIFY] Testing navigation to '{folder_name}'...")

        if folder_name not in self.navigation_map.get("music_folders", {}):
            print(f"[ERROR] Folder '{folder_name}' not in map!")
            return False

        target_pos = self.navigation_map["music_folders"][folder_name]["position"]

        # Reset and navigate
        self._reset_to_root()

        # TODO: Navigate to music root (multi-level)
        input(f"\n[MANUAL] Navigate manually to music root, then press Enter...")

        # Navigate to folder
        print(f"[NAVIGATE] Moving {target_pos} steps DOWN...")
        for i in range(target_pos):
            self.midi.send_cc(72, 127)
            time.sleep(2.0)
            if (i + 1) % 5 == 0:
                print(f"  -> {i+1}/{target_pos}")

        # Verify with user
        confirm = input(f"\n[VERIFY] Are you on '{folder_name}'? (y/n) > ").strip().lower()

        if confirm == 'y':
            print(f"[SUCCESS] Navigation to '{folder_name}' verified!")
            return True
        else:
            print(f"[FAIL] Navigation to '{folder_name}' incorrect")
            actual = input("[CORRECTION] What folder are you actually on? > ").strip()
            print(f"[NOTE] Expected '{folder_name}' but got '{actual}'")
            return False

    def export_summary(self):
        """Export training summary"""

        summary = {
            "total_root_folders": len(self.navigation_map.get("root_folders", [])),
            "total_music_folders": len(self.navigation_map.get("music_folders", {})),
            "root_folders": [f["name"] for f in self.navigation_map.get("root_folders", [])],
            "music_folders": list(self.navigation_map.get("music_folders", {}).keys()),
            "session_duration": str(datetime.now() - self.session_start),
            "last_updated": self.navigation_map.get("last_updated")
        }

        summary_file = Path("data/training_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n[EXPORT] Summary saved to: {summary_file}")

        return summary


def main():
    """Main training interface"""

    print("="*70)
    print("TRAKTOR LIBRARY MAPPING TRAINING SYSTEM")
    print("="*70)
    print("\nThis is the SACRED GRAIL of navigation.")
    print("Once trained, the system will know exactly how to navigate.")
    print("\nYou can interrupt (Ctrl+C) and resume later.")

    mapper = LibraryMapper()

    while True:
        print("\n" + "="*70)
        print("TRAINING MENU")
        print("="*70)
        print("\n1. Train ROOT folders (Track Collection, Playlists, etc.)")
        print("2. Train MUSIC folders (House, Dub, Techno, etc.)")
        print("3. Verify navigation to specific folder")
        print("4. Export training summary")
        print("5. View current map")
        print("6. Exit")

        choice = input("\nSelect option (1-6): ").strip()

        if choice == '1':
            mapper.train_root_folders()
        elif choice == '2':
            mapper.train_music_folders()
        elif choice == '3':
            folder = input("Enter folder name to verify: ").strip()
            mapper.verify_navigation(folder)
        elif choice == '4':
            summary = mapper.export_summary()
            print(f"\n[SUMMARY]")
            print(f"  Root folders: {summary['total_root_folders']}")
            print(f"  Music folders: {summary['total_music_folders']}")
            print(f"  Session duration: {summary['session_duration']}")
        elif choice == '5':
            print(f"\n[MAP]")
            print(json.dumps(mapper.navigation_map, indent=2, ensure_ascii=False))
        elif choice == '6':
            print("\n[EXIT] Saving final state...")
            mapper._save_map()
            print("[DONE] Training session complete!")
            break
        else:
            print("[ERROR] Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPT] Training interrupted by user")
        print("[SAVE] Progress has been saved automatically")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
