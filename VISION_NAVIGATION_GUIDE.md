# Vision-Guided Browser Navigation - Complete Guide

## Overview

The Traktor DJ AI system now includes **vision-guided browser navigation** - the ability to intelligently navigate through Traktor's file browser tree using Claude Vision API to read folder names and find target folders.

## How It Works

### 1. Natural Language Commands
Users can type commands like:
- "naviga fino alla cartella dub"
- "Navigate to the techno folder"
- "trova la cartella house"

### 2. Command Flow
```
User Command
    ↓
OpenRouter LLM (DeepSeek) - Parses command
    ↓
Extracts: action=NAVIGATE_FOLDER, folder="dub"
    ↓
workflow_controller.py - Routes to navigation action
    ↓
BrowserNavigator - Vision-guided navigation
    ↓
1. Capture screenshot
2. Claude Vision API - Read folder names
3. Calculate navigation steps
4. MIDI commands - Navigate up/down/expand
5. Verify arrival at target
    ↓
Success/Failure response to user
```

## Key Components

### 1. **BrowserNavigator** (`autonomous_dj/browser_navigator.py`)
The core navigation engine that:
- Captures screenshots of Traktor browser
- Uses Claude Vision API to read folder names
- Implements intelligent pathfinding algorithm
- Executes MIDI navigation commands
- Verifies arrival at target folder

**Key Methods:**
- `get_current_browser_state()` - Vision analysis of browser tree
- `navigate_to_folder(target_folder, max_attempts)` - Main navigation method
- `search_and_navigate(search_terms)` - Multi-term search

### 2. **MIDI Browser Commands** (`traktor_midi_driver.py`)
MIDI CC commands for browser control:
- `browser_navigate_up()` - CC 73: Navigate up in tree
- `browser_navigate_down()` - CC 72: Navigate down in tree
- `browser_expand_collapse()` - CC 64: Expand/collapse nodes
- `browser_scroll_tracks()` - CC 74: Scroll through track list

### 3. **Command Parsing** (`autonomous_dj/openrouter_client.py`)
OpenRouter DeepSeek LLM recognizes NAVIGATE_FOLDER action:

**Input:** "naviga fino alla cartella dub"

**Output:**
```json
{
    "action": "NAVIGATE_FOLDER",
    "folder": "dub",
    "confidence": 0.95,
    "reasoning": "Clear navigation command to dub folder"
}
```

### 4. **Workflow Integration** (`autonomous_dj/workflow_controller.py`)
The main controller orchestrates:
- Command parsing (OpenRouter)
- Vision analysis (Claude Vision)
- Navigation execution (BrowserNavigator)
- MIDI control (TraktorMIDIDriver)
- Safety checks (TraktorSafetyChecks)

## Navigation Algorithm

```python
def navigate_to_folder(target_folder, max_attempts=20):
    for attempt in range(max_attempts):
        # 1. Get current state using vision
        state = get_current_browser_state()
        current_folder = state['current_folder']
        visible_folders = state['visible_folders']

        # 2. Check if already at target
        if current_folder == target_folder:
            return True

        # 3. Check if target is visible
        if target_folder in visible_folders:
            # Calculate steps needed
            steps = visible_folders.index(target) - visible_folders.index(current)

            # Navigate up or down
            if steps > 0:
                for _ in range(steps):
                    browser_navigate_down()
            else:
                for _ in range(abs(steps)):
                    browser_navigate_up()

            # Verify arrival
            if get_current_folder() == target_folder:
                return True

        # 4. Target not visible - expand and explore
        browser_expand_collapse()
        browser_navigate_down()  # Explore deeper

    return False
```

## Vision Prompt

The system uses this specialized prompt for Claude Vision:

```
Analyze the Traktor browser tree on the left side.

Focus on:
1. What is the currently selected/highlighted folder in the tree?
2. What folders are visible in the tree (expanded or collapsed)?
3. Is the tree expanded or collapsed?

Return ONLY JSON format:
{
    "current_folder": "name of currently selected folder or null",
    "visible_folders": ["folder1", "folder2", ...],
    "tree_expanded": true/false
}

Be precise with folder names. Common folders: Root, Collection, Playlists, iTunes,
Audio Recordings, Dub, Techno, House, etc.
```

## Testing

### Method 1: Standalone Test Script
```bash
# Run comprehensive test
TEST_BROWSER_NAVIGATION.bat

# Or with Python directly:
.\venv\Scripts\python.exe test_browser_navigation.py
```

**Test Sequence:**
1. Browser state detection test
2. Natural language command test
3. Direct navigation test

### Method 2: Via Web Frontend
```bash
# Start production server
RUN_PRODUCTION_SERVER.bat

# Open browser: http://localhost:8000
# Type command: "naviga fino alla cartella dub"
```

### Method 3: Direct Python API
```python
from autonomous_dj.workflow_controller import DJWorkflowController

controller = DJWorkflowController()

# Test navigation
result = controller.handle_user_command("Navigate to the techno folder")
print(result['response'])

controller.cleanup()
```

## Configuration

### Required API Keys (`autonomous_dj/config.py`)
```python
ANTHROPIC_API_KEY = "sk-ant-api03-..."  # Claude Vision API
OPENROUTER_API_KEY = "sk-or-v1-..."    # OpenRouter (DeepSeek free)
```

### Navigation Parameters
Adjust in `browser_navigator.py`:
- `max_attempts=20` - Maximum navigation attempts
- `time.sleep(0.3)` - Delay between MIDI commands
- `time.sleep(0.5)` - Delay after expand/collapse

## Error Handling

### Common Issues

**1. Folder Not Found**
```
Response: "Non riesco a trovare la cartella 'xyz'. Prova a posizionarti
manualmente piu vicino."
```
**Solutions:**
- Folder may not exist
- Folder may be too deeply nested
- Try starting from a closer parent folder

**2. Vision Analysis Failed**
```
Error: [BROWSER NAV] Error analyzing browser: ...
```
**Solutions:**
- Check Traktor window is visible
- Verify browser is expanded (not minimized)
- Check Claude API key is valid

**3. MIDI Commands Not Working**
```
Error: MIDI connection lost
```
**Solutions:**
- Verify loopMIDI is running
- Check Traktor MIDI settings
- Restart Traktor with ASIO (not WASAPI)

## Performance

- **Vision Analysis**: ~1-2 seconds per screenshot
- **Navigation Step**: ~300ms per MIDI command
- **Average Navigation**: 5-10 seconds for typical folder
- **Max Attempts**: 20 (configurable)

## Integration with Frontend

The vision navigation is fully integrated with the web frontend:

**Frontend → Backend Flow:**
1. User types: "naviga alla cartella dub"
2. WebSocket sends command to `/ws/chat`
3. Backend calls `workflow_controller.handle_user_command()`
4. OpenRouter parses: `action=NAVIGATE_FOLDER, folder="dub"`
5. BrowserNavigator executes with vision
6. WebSocket streams progress updates
7. Final result sent to frontend

**Progress Updates:**
```javascript
// Frontend receives real-time updates:
{
    "type": "progress",
    "message": "[BROWSER NAV] Attempt 3/15"
}
{
    "type": "progress",
    "message": "[BROWSER NAV] Target visible, navigating to it..."
}
{
    "type": "result",
    "success": true,
    "message": "Navigato alla cartella 'dub' usando vision AI"
}
```

## Future Improvements

### Planned Features
- [ ] Cache folder tree structure to reduce vision API calls
- [ ] Fuzzy matching for folder names (e.g., "Dub" matches "dub", "DUB")
- [ ] Multi-level navigation (e.g., "Playlists/Techno/Dark")
- [ ] Smart folder suggestions based on history
- [ ] Breadcrumb tracking for faster return navigation

### Performance Optimizations
- [ ] Reduce vision API calls with intelligent caching
- [ ] Parallel vision analysis while navigating
- [ ] Adaptive delay based on Traktor response time

## Technical Details

### File Structure
```
C:/traktor/
├── autonomous_dj/
│   ├── browser_navigator.py          # Vision-guided navigation engine
│   ├── workflow_controller.py        # Main orchestrator
│   ├── openrouter_client.py          # LLM command parsing
│   ├── claude_vision_client.py       # Vision API wrapper
│   └── config.py                     # API keys
├── traktor_midi_driver.py            # MIDI control
├── test_browser_navigation.py        # Test script
├── TEST_BROWSER_NAVIGATION.bat       # Test launcher
└── VISION_NAVIGATION_GUIDE.md        # This file
```

### Dependencies
- **Claude Vision API**: UI screenshot analysis
- **OpenRouter DeepSeek**: Natural language parsing
- **mido + python-rtmidi**: MIDI communication
- **mss**: Multi-screen screenshot capture
- **Pillow**: Image processing

## Troubleshooting Checklist

Before testing navigation:
- [ ] Traktor Pro 3 is running
- [ ] Browser is visible (left side of UI)
- [ ] loopMIDI configured: "Traktor MIDI Bus 1"
- [ ] Traktor audio: ASIO (NOT WASAPI)
- [ ] MIDI Interaction Mode: "Direct" (NOT Toggle/Hold)
- [ ] API keys configured in `autonomous_dj/config.py`
- [ ] Python dependencies installed: `pip install -r requirements.txt`

## Support

For issues or questions:
1. Check logs in console output
2. Run `verify_midi_setup.py` to test MIDI connection
3. Test vision with `test_vision_simple.py`
4. Review `.claude/skills/traktor-dj-autonomous/SKILL.md`

---

**Last Updated:** 2025-10-25
**Status:** Production Ready ✓
**Version:** 1.0
