# Traktor Pro 3 - MIDI CC Mapping Reference

**Version**: 2.0
**Last Updated**: 2025-10-23
**Verified From**: Traktor screenshots (2025-10-08, 2025-10-21)
**Source**: command_mapping_ok.tsi

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Transport Controls](#transport-controls)
3. [Track Loading](#track-loading)
4. [Mixer Controls](#mixer-controls)
5. [Browser Navigation](#browser-navigation)
6. [Loop Controls](#loop-controls)
7. [Effects (FX)](#effects-fx)
8. [Python Usage Examples](#python-usage-examples)
9. [Critical Notes](#critical-notes)

---

## Quick Reference

### Most Common Operations

| Operation | Deck A | Deck B | Python Constant |
|-----------|--------|--------|-----------------|
| **Play/Pause** | CC 47 | CC 48 | `TraktorCC.DECK_A_PLAY_PAUSE` |
| **Load Track** | CC 43 | CC 44 | `TraktorCC.DECK_A_LOAD_TRACK` |
| **Cue** | CC 80 | CC 81 | `TraktorCC.DECK_A_CUE` |
| **Sync On** | CC 69 | CC 42 | `TraktorCC.DECK_A_SYNC_ON` |
| **Volume** | CC 65 | CC 60 | `TraktorCC.DECK_A_VOLUME` |

**Browser**:
- Scroll list: CC 74
- Scroll tree down: CC 72
- Scroll tree up: CC 73

**Master**:
- Master volume: CC 75

---

## Transport Controls

### Play/Pause

| Deck | CC | Python Constant | Value Range |
|------|----|----|-------------|
| A | 47 | `DECK_A_PLAY_PAUSE` | 0=Pause, 127=Play |
| B | 48 | `DECK_B_PLAY_PAUSE` | 0=Pause, 127=Play |
| C | 90 | `DECK_C_PLAY_PAUSE` | 0=Pause, 127=Play |
| D | 91 | `DECK_D_PLAY_PAUSE` | 0=Pause, 127=Play |

**Usage**:
```python
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC

midi = TraktorMIDIDriver()
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)  # Play
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 0)    # Pause
```

### Cue Points

| Deck | CC | Python Constant | Behavior |
|------|----|----|----------|
| A | 80 | `DECK_A_CUE` | Jump to cue, play while held |
| B | 81 | `DECK_B_CUE` | Jump to cue, play while held |
| C | 82 | `DECK_C_CUE` | Jump to cue, play while held |
| D | 83 | `DECK_D_CUE` | Jump to cue, play while held |

### Sync Controls

#### Sync On/Off

| Deck | CC | Python Constant | Value |
|------|----|----|-------|
| A | 69 | `DECK_A_SYNC_ON` | 0=Off, 127=On |
| B | 42 | `DECK_B_SYNC_ON` | 0=Off, 127=On |
| C | 59 | `DECK_C_SYNC_ON` | 0=Off, 127=On |
| D | 63 | `DECK_D_SYNC_ON` | 0=Off, 127=On |

#### Sync Grid

| Deck | CC | Python Constant | Behavior |
|------|----|----|----------|
| A | 24 | `DECK_A_SYNC_GRID` | Sync to beat grid |
| B | 25 | `DECK_B_SYNC_GRID` | Sync to beat grid |

### Tempo Master

| Deck | CC | Python Constant | Value |
|------|----|----|-------|
| A | 33 | `DECK_A_TEMPO_MASTER` | 0=Off, 127=Master |
| B | 37 | `DECK_B_TEMPO_MASTER` | 0=Off, 127=Master |
| C | 38 | `DECK_C_TEMPO_MASTER` | 0=Off, 127=Master |
| D | 39 | `DECK_D_TEMPO_MASTER` | 0=Off, 127=Master |

⚠️ **Warning**: CC 33 may control pitch on some systems. Test before use.

### Tempo Adjust

| Deck | CC | Python Constant | Value Range |
|------|----|----|-------------|
| A | 41 | `DECK_A_TEMPO` | 0-127 (64=0%, 0=-100%, 127=+100%) |
| B | 40 | `DECK_B_TEMPO` | 0-127 (64=0%, 0=-100%, 127=+100%) |
| C | 2 | `DECK_C_TEMPO` | 0-127 (64=0%, 0=-100%, 127=+100%) |
| D | 3 | `DECK_D_TEMPO` | 0-127 (64=0%, 0=-100%, 127=+100%) |

---

## Track Loading

| Deck | CC | Python Constant | Behavior |
|------|----|----|----------|
| A | 43 | `DECK_A_LOAD_TRACK` | Load selected track |
| B | 44 | `DECK_B_LOAD_TRACK` | Load selected track |
| C | 45 | `DECK_C_LOAD_TRACK` | Load selected track |
| D | 46 | `DECK_D_LOAD_TRACK` | Load selected track |

**Typical Workflow**:
```python
# 1. Navigate browser to track
midi.send_cc(TraktorCC.BROWSER_SCROLL_LIST, 64)  # Scroll down

# 2. Load to deck
midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)

# 3. Wait for load (typically 500ms - 2s depending on track)
time.sleep(1)

# 4. Verify loaded (check waveform in Traktor)
```

---

## Mixer Controls

### Volume Faders

| Control | CC | Python Constant | Value Range |
|---------|----|----|-------------|
| Deck A | 65 | `DECK_A_VOLUME` | 0-127 (0=Silent, 127=Max) |
| Deck B | 60 | `DECK_B_VOLUME` | 0-127 (0=Silent, 127=Max) |
| Deck C | 61 | `DECK_C_VOLUME` | 0-127 (0=Silent, 127=Max) |
| Deck D | 62 | `DECK_D_VOLUME` | 0-127 (0=Silent, 127=Max) |
| Master | 75 | `MASTER_VOLUME` | 0-127 (0=Silent, 127=Max) |

**Recommended Values**:
- Playing deck: 85-100 (CC value ~108-127)
- Incoming deck (before mix): 0-20 (CC value ~0-26)
- Master: 85-95 (CC value ~108-121)

### EQ Controls

#### Deck A

| Band | CC | Python Constant | Value Range |
|------|----|----|-------------|
| High | 34 | `DECK_A_EQ_HIGH` | 0-127 (64=neutral, 0=kill, 127=boost) |
| Mid | 35 | `DECK_A_EQ_MID` | 0-127 (64=neutral, 0=kill, 127=boost) |
| Low | 36 | `DECK_A_EQ_LOW` | 0-127 (64=neutral, 0=kill, 127=boost) |

#### Deck B

| Band | CC | Python Constant | Value Range |
|------|----|----|-------------|
| High | 50 | `DECK_B_EQ_HIGH` | 0-127 (64=neutral) |
| Mid | 51 | `DECK_B_EQ_MID` | 0-127 (64=neutral) |
| Low | 52 | `DECK_B_EQ_LOW` | 0-127 (64=neutral) |

#### Deck C

| Band | CC | Python Constant | Value Range |
|------|----|----|-------------|
| High | 84 | `DECK_C_EQ_HIGH` | 0-127 (64=neutral) |
| Mid | 85 | `DECK_C_EQ_MID` | 0-127 (64=neutral) |
| Low | 86 | `DECK_C_EQ_LOW` | 0-127 (64=neutral) |

#### Deck D

| Band | CC | Python Constant | Value Range |
|------|----|----|-------------|
| High | 66 | `DECK_D_EQ_HIGH` | 0-127 (64=neutral) |
| Mid | 67 | `DECK_D_EQ_MID` | 0-127 (64=neutral) |
| Low | 68 | `DECK_D_EQ_LOW` | 0-127 (64=neutral) |

**EQ Mixing Technique**:
```python
# Transition: Fade out old track bass, fade in new track bass
# Old track (Deck A) - reduce low
midi.send_cc(TraktorCC.DECK_A_EQ_LOW, 0)  # Kill bass

# New track (Deck B) - boost low
midi.send_cc(TraktorCC.DECK_B_EQ_LOW, 64)  # Neutral bass
```

---

## Browser Navigation

| Function | CC | Python Constant | Direction | Value |
|----------|----|----|-----------|-------|
| Scroll List | 74 | `BROWSER_SCROLL_LIST` | Down | 64 |
| Scroll List | 74 | `BROWSER_SCROLL_LIST` | Up | 63 |
| Scroll Tree | 72 | `BROWSER_SCROLL_TREE_INC` | Down | 127 |
| Scroll Tree | 73 | `BROWSER_SCROLL_TREE_DEC` | Up | 127 |
| Expand/Collapse | 64 | `BROWSER_EXPAND_COLLAPSE` | Toggle | 127 |

⚠️ **CRITICAL**: Browser CC 72/73 move **2 folders at a time**, not 1!

**Delay Required**: 1.5-2 seconds between commands (Traktor ignores faster input)

**Example**:
```python
# Navigate to folder
midi.send_cc(TraktorCC.BROWSER_SCROLL_TREE_INC, 127)
time.sleep(2)  # REQUIRED DELAY

# Scroll through tracks
midi.send_cc(TraktorCC.BROWSER_SCROLL_LIST, 64)  # Down
time.sleep(2)

midi.send_cc(TraktorCC.BROWSER_SCROLL_LIST, 64)  # Down again
time.sleep(2)
```

---

## Loop Controls

### Deck A

| Function | CC | Python Constant | Behavior |
|----------|----|----|----------|
| Loop Active | 123 | `DECK_A_LOOP_ACTIVE` | Toggle loop on/off |
| Loop Out | 122 | `DECK_A_LOOP_OUT` | Set loop out point |
| Loop In/Set Cue | 121 | `DECK_A_LOOP_IN_SET_CUE` | Set loop in or cue |

### Deck B

| Function | CC | Python Constant | Behavior |
|----------|----|----|----------|
| Loop Active | 126 | `DECK_B_LOOP_ACTIVE` | Toggle loop on/off |
| Loop Out | 125 | `DECK_B_LOOP_OUT` | Set loop out point |
| Loop In/Set Cue | 124 | `DECK_B_LOOP_IN_SET_CUE` | Set loop in or cue |

### Deck C

| Function | CC | Python Constant | Behavior |
|----------|----|----|----------|
| Loop Active | 55 | `DECK_C_LOOP_ACTIVE` | Toggle loop on/off |
| Loop Out | 54 | `DECK_C_LOOP_OUT` | Set loop out point |
| Loop In/Set Cue | 53 | `DECK_C_LOOP_IN_SET_CUE` | Set loop in or cue |

### Deck D

| Function | CC | Python Constant | Behavior |
|----------|----|----|----------|
| Loop Active | 58 | `DECK_D_LOOP_ACTIVE` | Toggle loop on/off |
| Loop Out | 57 | `DECK_D_LOOP_OUT` | Set loop out point |
| Loop In/Set Cue | - | *(not mapped)* | N/A |

---

## Effects (FX)

### FX Unit 1

| Control | CC | Python Constant | Value |
|---------|----|----|-------|
| Unit On | 96 | `FX1_UNIT_ON` | 0=Off, 127=On |
| Button 1 | 93 | `FX1_BUTTON_1` | 0=Off, 127=On |
| Button 2 | 94 | `FX1_BUTTON_2` | 0=Off, 127=On |
| Button 3 | 95 | `FX1_BUTTON_3` | 0=Off, 127=On |
| Knob 1 | 77 | `FX1_KNOB_1` | 0-127 |
| Knob 2 | 78 | `FX1_KNOB_2` | 0-127 |
| Knob 3 | 79 | `FX1_KNOB_3` | 0-127 |
| Dry/Wet | 76 | `FX1_DRY_WET` | 0=Dry, 127=Wet |

### FX Unit 2

| Control | CC | Python Constant | Value |
|---------|----|----|-------|
| Unit On | 104 | `FX2_UNIT_ON` | 0=Off, 127=On |
| Button 1 | 101 | `FX2_BUTTON_1` | 0=Off, 127=On |
| Button 2 | 102 | `FX2_BUTTON_2` | 0=Off, 127=On |
| Button 3 | 103 | `FX2_BUTTON_3` | 0=Off, 127=On |
| Knob 1 | 98 | `FX2_KNOB_1` | 0-127 |
| Knob 2 | 99 | `FX2_KNOB_2` | 0-127 |
| Knob 3 | 100 | `FX2_KNOB_3` | 0-127 |
| Dry/Wet | 97 | `FX2_DRY_WET` | 0=Dry, 127=Wet |

### FX Unit 3

| Control | CC | Python Constant | Value |
|---------|----|----|-------|
| Unit On | 112 | `FX3_UNIT_ON` | 0=Off, 127=On |
| Button 1 | 109 | `FX3_BUTTON_1` | 0=Off, 127=On |
| Button 2 | 110 | `FX3_BUTTON_2` | 0=Off, 127=On |
| Button 3 | 111 | `FX3_BUTTON_3` | 0=Off, 127=On |
| Knob 1 | 106 | `FX3_KNOB_1` | 0-127 |
| Knob 2 | 107 | `FX3_KNOB_2` | 0-127 |
| Knob 3 | 108 | `FX3_KNOB_3` | 0-127 |
| Dry/Wet | 105 | `FX3_DRY_WET` | 0=Dry, 127=Wet |

### FX Unit 4

| Control | CC | Python Constant | Value |
|---------|----|----|-------|
| Unit On | 120 | `FX4_UNIT_ON` | 0=Off, 127=On |
| Button 1 | 117 | `FX4_BUTTON_1` | 0=Off, 127=On |
| Button 2 | 118 | `FX4_BUTTON_2` | 0=Off, 127=On |
| Button 3 | 119 | `FX4_BUTTON_3` | 0=Off, 127=On |
| Knob 1 | 114 | `FX4_KNOB_1` | 0-127 |
| Knob 2 | 115 | `FX4_KNOB_2` | 0-127 |
| Knob 3 | 116 | `FX4_KNOB_3` | 0-127 |
| Dry/Wet | 113 | `FX4_DRY_WET` | 0=Dry, 127=Wet |

---

## Python Usage Examples

### Basic Setup

```python
from traktor_midi_driver import TraktorMIDIDriver, TraktorCC
import time

# Initialize driver
midi = TraktorMIDIDriver()  # Auto-detects "Traktor MIDI Bus 1"

# Or use dry-run for testing
midi = TraktorMIDIDriver(dry_run=True)  # Logs but doesn't send
```

### Load and Play Track

```python
# Load track to Deck A
midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
time.sleep(1)  # Wait for load

# Set volume
midi.send_cc(TraktorCC.DECK_A_VOLUME, 108)  # ~85%

# Play
midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
```

### Sync Two Decks

```python
# Deck A is MASTER (already playing)
midi.send_cc(TraktorCC.DECK_A_TEMPO_MASTER, 127)

# Deck B syncs to Deck A
midi.send_cc(TraktorCC.DECK_B_SYNC_ON, 127)
midi.send_cc(TraktorCC.DECK_B_VOLUME, 26)  # Start low (20%)
midi.send_cc(TraktorCC.DECK_B_PLAY_PAUSE, 127)

# Gradual volume transition
for vol in range(26, 108, 10):  # 20% -> 85%
    midi.send_cc(TraktorCC.DECK_B_VOLUME, vol)
    time.sleep(0.5)
```

### Browser Navigation

```python
# Navigate folder tree down (2 folders)
midi.send_cc(TraktorCC.BROWSER_SCROLL_TREE_INC, 127)
time.sleep(2)  # CRITICAL DELAY

# Scroll track list down
midi.send_cc(TraktorCC.BROWSER_SCROLL_LIST, 64)
time.sleep(2)  # CRITICAL DELAY

# Load to deck
midi.send_cc(TraktorCC.DECK_A_LOAD_TRACK, 127)
```

### Apply Effects

```python
# Enable FX Unit 1
midi.send_cc(TraktorCC.FX1_UNIT_ON, 127)

# Activate effect button 1 (e.g., Reverb)
midi.send_cc(TraktorCC.FX1_BUTTON_1, 127)

# Adjust dry/wet mix
midi.send_cc(TraktorCC.FX1_DRY_WET, 64)  # 50% wet

# Adjust effect parameter
midi.send_cc(TraktorCC.FX1_KNOB_1, 90)
```

### Context Manager Pattern

```python
with TraktorMIDIDriver() as midi:
    # Automatically closes connection when done
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 127)
    time.sleep(5)
    midi.send_cc(TraktorCC.DECK_A_PLAY_PAUSE, 0)
# Connection auto-closed
```

---

## Critical Notes

### 1. MIDI Interaction Mode (CRITICAL!)

⚠️ **MUST be set to "Direct" mode!**

**Problem**: Toggle/Hold modes make MIDI commands unpredictable
**Solution**: Set ALL controls to "Direct" interaction mode

**How to fix**:
1. Preferences → Controller Manager
2. Select Generic MIDI device
3. For EACH control (Play, Load, Sync, Volume, etc.)
4. Set **Interaction Mode = "Direct"**

**Why this matters**:
- **Direct**: CC 127 = Action ON, CC 0 = Action OFF (predictable)
- **Toggle**: Each CC toggles state (unpredictable)
- **Hold**: Only active while CC > 0 (not suitable)

**See**: `MIDI_INTERACTION_MODE_FIX.md` for complete details

### 2. ASIO Driver Requirement

⚠️ **WASAPI blocks MIDI!**

- Traktor's audio device MUST be set to **ASIO**
- WASAPI (Windows default) blocks MIDI processing
- Install **ASIO4ALL** if no native ASIO driver available
- Restart Traktor after changing audio device

**Check**: Preferences → Audio Setup → Audio Device

### 2. Browser Navigation Behavior

⚠️ **CC 72/73 move 2 folders, not 1**

- Single CC 72 command = move down 2 folders
- Single CC 73 command = move up 2 folders
- Compensation required for precise navigation
- Delay: 1.5-2 seconds between commands (Traktor ignores faster input)

### 3. Tempo Master vs Pitch

⚠️ **CC 33 behavior varies**

- On most systems: CC 33 = TEMPO MASTER
- On some systems: CC 33 = PITCH control
- **Always test** CC 33 before production use
- If incorrect, use alternative control mapping

### 4. loopMIDI Configuration

**Windows Setup**:
1. Install loopMIDI
2. Create port: "Traktor MIDI Bus 1"
3. In Traktor: Preferences → Controller Manager → Add Generic MIDI
4. Map input/output to "Traktor MIDI Bus 1"

**macOS Setup**:
1. Audio MIDI Setup → Window → Show MIDI Studio
2. Double-click "IAC Driver"
3. Enable "Device is online"
4. Create port: "Driver IAC Bus 1"

### 5. Command Latency

- Target: <10ms latency
- Browser commands: 1.5-2s delay required
- Track load: Allow 500ms-2s for completion
- Mixer/transport: Near-instant response

### 6. Value Ranges

Most CC values use full MIDI range (0-127):

- **Binary controls** (Play, Sync, etc.): 0=Off, 127=On
- **Continuous controls** (Volume, EQ): 0=Min, 64=Neutral, 127=Max
- **Direction controls** (Browser): 63=Up, 64=Down

---

## Files Reference

```
C:\traktor\
├── traktor_midi_driver.py              # Main MIDI driver
├── config/
│   └── traktor_midi_mapping.json       # Configuration file
├── verify_midi_sync.py                 # Synchronization checker
├── MIDI_MAPPING_REFERENCE.md           # This file
└── MIDI_SYNC_REPORT.md                 # Sync verification report
```

---

## Verification Status

✅ **All mappings verified and synchronized**

- Last verification: 2025-10-23
- Verification tool: `verify_midi_sync.py`
- Result: 31/31 mappings match
- Status: **PRODUCTION READY**

---

**Document Version**: 2.0
**Last Updated**: 2025-10-23
**Maintained By**: DJ Fiore AI System
