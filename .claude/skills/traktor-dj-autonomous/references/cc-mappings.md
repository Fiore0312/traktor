# Traktor Pro 3 Control Change (CC) Mappings Reference

## Source of Truth

File: `traktor_midi_driver.py`
Status: ✅ Verified 2025-10-22
Total Mappings: 100+

## Deck A Control

### Playback Control
- **Play/Pause**: CC 47
- **Cue**: CC 49
- **Cup (Cue+Play)**: CC 51
- **Load Track**: CC 43

### Volume & Mixing
- **Volume**: CC 65
- **Tempo Master**: CC 33 (⚠️ May control pitch instead)
- **Sync On**: CC 69
- **Sync Off**: CC 71

### EQ Controls
- **EQ Low**: CC 36
- **EQ Mid**: CC 35
- **EQ High**: CC 34
- **Gain**: CC 37

### Loop Controls
- **Loop Active On**: CC 52
- **Loop Active Off**: CC 53
- **Loop Size Double**: CC 54
- **Loop Size Halve**: CC 55

### Hotcue System
- **Hotcue 1 Store**: CC 2 (CONFLICT RESOLVED: Use 87)
- **Hotcue 2 Store**: CC 3 (CONFLICT RESOLVED: Use 88)
- **Hotcue 3 Store**: CC 4 (CONFLICT RESOLVED: Use 89)
- **Hotcue 4 Store**: CC 5
- **Hotcue 5 Store**: CC 6
- **Hotcue 6 Store**: CC 7
- **Hotcue 7 Store**: CC 8
- **Hotcue 8 Store**: CC 9

## Deck B Control

### Playback Control
- **Play/Pause**: CC 48
- **Cue**: CC 50
- **Load Track**: CC 44

### Volume & Mixing
- **Volume**: CC 60
- **Sync On**: CC 70

### EQ Controls
- **EQ Low**: CC 40
- **EQ Mid**: CC 39
- **EQ High**: CC 38

## Mixer Controls

### Master Section
- **Crossfader**: CC 8
- **Master Volume**: CC 10

### Effects
- **FX Unit 1 On/Off**: CC 11
- **FX Unit 2 On/Off**: CC 12
- **FX Unit 3 On/Off**: CC 13
- **FX Unit 4 On/Off**: CC 14

## Browser Navigation

⚠️ **CRITICAL TIMING**: 1.5-2 seconds between commands required

- **Scroll Tree Down**: CC 72 (⚠️ Moves 2 positions per command)
- **Scroll Tree Up**: CC 73 (⚠️ Moves 2 positions per command)
- **Expand/Collapse**: CC 64
- **Scroll List**: CC 74

### Browser Behavior Notes

1. **2x Movement Issue**: CC 72/73 move 2 folders per command
   - Compensation required in navigation logic
   - See `browser_navigation_knowledge.json`

2. **Timing Requirements**:
   - Minimum 1.5s delay between commands
   - Commands <1s apart are ignored
   - Optimal delay: 1.8-2.0s

## Known Issues

### Issue #1: Browser 2x Movement
**Status**: Documented
**Impact**: High
**Description**: CC 72/73 navigate 2 folders per command instead of 1

**Solution**:
```python
def navigate_to_position(target_position, current_position=1):
    steps_needed = (target_position - current_position) // 2
    for _ in range(steps_needed):
        send_cc(72, 127)  # Scroll down
        time.sleep(1.8)   # Wait for Traktor
```

### Issue #2: CC 33 May Control Pitch
**Status**: Unresolved
**Impact**: Medium
**Description**: CC 33 documented as MASTER but may control pitch instead

**Workaround**: Test CC 33 behavior before using in production

### Issue #3: WASAPI Blocks MIDI
**Status**: Resolved
**Impact**: Critical
**Description**: WASAPI audio driver blocks MIDI communication

**Solution**: Use ASIO audio driver
1. Install ASIO4ALL
2. Traktor → Audio Setup → Audio Device: ASIO4ALL v2
3. Sample Rate: 48000 Hz, Latency: ~42ms

## MIDI Channel Configuration

- **AI_CONTROL**: Channel 1 (for commands)
- **STATUS_FEEDBACK**: Channel 2 (for status, if supported)

## Value Ranges

Most CC values use:
- **0**: Off/Minimum
- **127**: On/Maximum
- **64**: Center/Neutral (for EQ, crossfader)

## Testing Commands

### Quick MIDI Test
```python
import rtmidi

midi_out = rtmidi.MidiOut()
ports = midi_out.get_ports()
print(ports)  # Should show "Traktor MIDI Bus 1"

# Open port
midi_out.open_port(ports.index("Traktor MIDI Bus 1"))

# Test play/pause on Deck A
midi_out.send_message([0xB0, 47, 127])  # CC 47, value 127

midi_out.close_port()
```

### Full System Test
```bash
python verify_midi_setup.py
```

## Additional Resources

- Official Traktor Manual: See project root
- TSI Mapping File: `command_mapping_ok.tsi` (source of mappings)
- MIDI Monitor Tool: `tools/midi_monitor.py` (if available)

---

**Last Verified**: 2025-10-22
**Test System**: Windows 10, loopMIDI, Traktor Pro 3
**Test Results**: 100+ CC mappings verified and working
