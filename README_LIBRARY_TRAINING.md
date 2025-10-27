# 📚 Library Training System - Documentation

## Overview

This is the **SACRED GRAIL** of the autonomous navigation system. Once trained, the system knows EXACTLY how to navigate your Traktor library without any vision or guesswork.

## What It Does

The training system creates a precise map of your Traktor browser structure by:

1. **Interactive Training** - You confirm each folder name
2. **Position Tracking** - Records exact UP/DOWN steps needed
3. **Persistent Storage** - Saves to JSON + SQLite database
4. **Resume Capability** - Can interrupt and continue anytime
5. **Auto-Backup** - Creates backup before every save
6. **Auto-Save** - Saves progress every 5 folders

## Files Created

### Primary Storage
- **`data/navigation_map.json`** - Main navigation map (human-readable)
  ```json
  {
    "version": "1.0",
    "root_folders": [
      {"name": "Track Collection", "position": 0, "has_children": true},
      {"name": "Playlists", "position": 1, "has_children": true},
      {"name": "Explorer", "position": 2, "has_children": true}
    ],
    "music_folders": {
      "House": {"position": 24, "parent_path": "...", "approximate_tracks": 30},
      "Dub": {"position": 12, "parent_path": "...", "approximate_tracks": 87}
    }
  }
  ```

### Backup Storage
- **`data/navigation_map.db`** - SQLite database backup
- **`data/backups/navigation_map_backup_YYYYMMDD_HHMMSS.json`** - Timestamped backups

### Summary
- **`data/training_summary.json`** - Training session summary

## How To Use

### Method 1: Double-Click Launcher
```batch
# Just double-click:
TRAIN_LIBRARY.bat
```

### Method 2: Command Line
```bash
cd C:\traktor
.\venv\Scripts\python.exe training_library_mapper.py
```

## Training Process

### Phase 1: Root Folders (10-15 minutes)

Maps top-level folders:
- Track Collection
- All Tracks
- All Stems
- Playlists
- Explorer
- etc.

**Process**:
1. System resets to root
2. System collapses all folders
3. For each position:
   - System asks: "What folder do you see?"
   - You type exact name: `Explorer`
   - System asks: "Has subfolders?" (y/n)
   - You confirm: `y`
   - System saves and moves DOWN

**Commands**:
- Type folder name → Save and move down
- `skip` → Move down without saving
- `done` → Finish this phase

### Phase 2: Music Folders (20-40 minutes)

Maps genre folders (House, Dub, Techno, etc.)

**IMPORTANT**: You must manually navigate to music folders first:
1. In Traktor: Explorer → Music Folders → C:\Users\Utente\Music
2. Expand the folder to show all genres
3. Position on first genre (e.g., "Ableton")
4. Then start training

**Process**:
1. System asks: "What music folder at position 0?"
2. You type: `Ableton`
3. System asks: "Approximately how many tracks?"
4. You type: `0` (or skip)
5. System saves and moves DOWN
6. Repeat for all folders

**Commands**:
- Type folder name → Save and move down
- `skip` → Move down without saving
- `back` → Move UP one position
- `done` → Finish this phase

**Auto-Save**: Progress saved every 5 folders

**Resume**: If you have existing folders, system asks if you want to resume from last position

### Phase 3: Verification (5-10 minutes)

Test navigation to specific folders:

1. Select option 3 from menu
2. Enter folder name: `House`
3. System navigates automatically
4. You confirm if correct

## Menu Options

```
1. Train ROOT folders (Track Collection, Playlists, etc.)
2. Train MUSIC folders (House, Dub, Techno, etc.)
3. Verify navigation to specific folder
4. Export training summary
5. View current map
6. Exit
```

## Interrupting & Resuming

### To Interrupt
Press `Ctrl+C` at any time

Progress is automatically saved:
- After each folder
- Every 5 folders (auto-save)
- On exit

### To Resume
1. Run `TRAIN_LIBRARY.bat` again
2. Select same phase (1 or 2)
3. System detects existing data
4. Choose "Resume from last? (y/n)"
5. System continues from last position

## Example Session

```
TRAKTOR LIBRARY MAPPING TRAINING SYSTEM
=======================================

TRAINING MENU
1. Train ROOT folders
2. Train MUSIC folders
3. Verify navigation
4. Export summary
5. View map
6. Exit

Select option: 2

PHASE 2: MUSIC FOLDER MAPPING
=======================================

[RESUME] Found 12 existing folders. Resume from last? (y/n) > y
[RESUME] Starting from position 12
[MOVE] Moving to position 12...

MUSIC FOLDER POSITION 12

[Q] What music folder do you see at position 12?
    (or 'done', 'skip', 'back')
    > Dub

[CONFIRM] Is 'Dub' correct? (y/n/retry) > y

[Q] Approximately how many tracks in 'Dub'? > 87

[SAVED] 'Dub' -> position 12 (~87 tracks)

[MOVE] Moving down to position 13...

...

[AUTO-SAVE] Progress saved (15 folders)
```

## Safety Features

### Automatic Backups
- Before loading existing map
- Stored in `data/backups/`
- Timestamped filenames
- Keep indefinitely (manual cleanup)

### Dual Storage
- **JSON** - Primary, human-readable, easy to edit
- **SQLite** - Backup, queryable, robust

### Validation
- Confirm each entry before saving
- Retry option for mistakes
- Correction option if wrong

### Resume Points
- Every folder saved immediately
- Auto-save every 5 folders
- Exit saves current state

## Integration with Navigator

Once trained, update the navigator to use the map:

```python
from pathlib import Path
import json

# Load trained map
map_file = Path("data/navigation_map.json")
with open(map_file) as f:
    navigation_map = json.load(f)

# Use positions
house_position = navigation_map["music_folders"]["House"]["position"]
# Navigate house_position steps DOWN from music root
```

## Future UI Integration

Planned "Sync Library" button in web UI:

```javascript
// In frontend/index.html
<button onclick="startLibrarySync()">
    Sync Library
</button>

// Calls API endpoint:
POST /api/sync-library
{
  "action": "start_training",
  "phase": "music_folders"
}
```

## Troubleshooting

### "Folder not found in map"
→ Run training for that folder

### "Position seems wrong"
→ Run verification (option 3)
→ Re-train if needed

### "Progress not saved"
→ Check `data/navigation_map.json` exists
→ Check file permissions

### "Can't resume"
→ Delete `data/navigation_map.json`
→ Start fresh training

## Best Practices

1. **Do in one session if possible** - Reduces inconsistencies
2. **Don't modify Traktor library during training** - Positions will change
3. **Keep backups** - `data/backups/` folder
4. **Verify after training** - Test 3-5 folders (option 3)
5. **Re-train if library changes** - Added/removed folders

## Performance

- **Root folders**: ~10-15 minutes (10-15 folders)
- **Music folders**: ~20-40 minutes (40-50 folders)
- **Total training time**: 30-60 minutes
- **Once trained**: PERMANENT (until library changes)

## Data Format

### navigation_map.json
```json
{
  "version": "1.0",
  "created_at": "2025-10-27T...",
  "last_updated": "2025-10-27T...",

  "root_folders": [
    {
      "name": "Track Collection",
      "position": 0,
      "has_children": true,
      "created_at": "2025-10-27T..."
    }
  ],

  "music_folders": {
    "House": {
      "position": 24,
      "parent_path": "Explorer > Music Folders > ...",
      "approximate_tracks": 30,
      "created_at": "2025-10-27T..."
    }
  },

  "navigation_history": [],
  "training_sessions": []
}
```

## Conclusion

This training system ensures:
- ✅ 100% accurate navigation
- ✅ No guesswork or vision needed
- ✅ Permanent knowledge of library
- ✅ Resume capability for long sessions
- ✅ Automatic backups
- ✅ Easy to update when library changes

**Once trained, this becomes the foundation of autonomous navigation forever.**

---

**Version**: 1.0
**Created**: 2025-10-27
**Status**: PRODUCTION READY
