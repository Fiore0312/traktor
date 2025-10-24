# Troubleshooting Guide

## Common Issues and Solutions

### 1. MIDI Not Working

#### Symptom
Traktor ignores all MIDI commands, loopMIDI shows activity but nothing happens

#### Root Cause
WASAPI audio driver blocks MIDI message processing

#### Solution
1. Open Traktor Pro 3
2. File → Preferences → Audio Setup
3. Change **Audio Device** from WASAPI to ASIO:
   - Install ASIO4ALL: http://www.asio4all.org/
   - Select "ASIO4ALL v2" as Audio Device
4. Click **Settings** button → Enable your audio interface
5. Sample Rate: 48000 Hz, Latency: 480 (~42ms)
6. Click **Apply** and restart Traktor

#### Verification
```bash
python verify_midi_setup.py
# Should see: "Deck A responding to MIDI commands"
```

### 2. Browser Navigation Not Working

#### Symptom
Browser commands don't move selection or move incorrectly

#### Root Cause A: Commands Too Fast
Traktor requires 1.5-2s between browser navigation commands

**Solution**:
```python
# ❌ Wrong: Too fast
for i in range(3):
    scroll_down(1)
    time.sleep(0.5)  # TOO FAST - Traktor ignores

# ✅ Correct: Proper timing
for i in range(3):
    scroll_down(1)
    time.sleep(1.8)  # Traktor can process
```

#### Root Cause B: 2x Movement Compensation Not Applied
CC 72/73 move 2 folders per command, not 1

**Solution**:
```python
def navigate_to_folder(target_position, current_position=1):
    # Calculate steps with 2x compensation
    distance = target_position - current_position
    steps = distance // 2  # Divide by 2 for compensation
    
    for i in range(steps):
        send_cc(72, 127)  # Scroll down
        time.sleep(1.8)
```


### 3. Both Decks Show MASTER Active

#### Symptom
Checking deck states shows both deck A and B have MASTER=ON

#### Root Cause
Manual MASTER commands during transition conflict with AUTO mode

#### Solution
```python
from autonomous_dj.generated.deck_operations import get_deck_state, set_master

# Check current state
state_a = get_deck_state('A')
state_b = get_deck_state('B')

print(f"Deck A MASTER: {state_a.get('master')}")
print(f"Deck B MASTER: {state_b.get('master')}")

# Fix: Keep highest volume deck as MASTER
if state_a['master'] and state_b['master']:
    if state_a['volume'] > state_b['volume']:
        set_master('B', False)
    else:
        set_master('A', False)
```

#### Prevention
Let AUTO mode handle MASTER transfer. Don't send manual MASTER commands during transitions.

### 4. No Sound from Deck

#### Symptom
Deck is playing (waveform moving) but no audio output

#### Possible Causes & Solutions

**A. Crossfader on Wrong Side**
```python
# Check crossfader position
position = get_crossfader_position()
print(f"Crossfader at: {position}")

# Fix: Move to correct side
if playing_deck == 'A':
    set_crossfader_position('left')
else:
    set_crossfader_position('right')
```

**B. Volume Fader Too Low**
```python
# Check and fix volume
volume = get_volume(deck)
if volume < 10:
    set_volume(deck, 85)  # Set to audible level
```

**C. EQ Killed**
```python
# Check EQ settings
eq_low = get_eq(deck, 'low')
eq_mid = get_eq(deck, 'mid')
eq_high = get_eq(deck, 'high')

# Reset to neutral if killed
if any(level < 20 for level in [eq_low, eq_mid, eq_high]):
    set_eq(deck, 'low', 64)   # Neutral
    set_eq(deck, 'mid', 64)
    set_eq(deck, 'high', 64)
```

### 5. LLM Integration Errors

#### Symptom
```
Error: OpenRouter API key not found
```

#### Solution
Create `.env` file in project root:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

#### Symptom
```
Error: ChromaDB database not found
```

#### Solution
Initialize persistent memory:
```python
from autonomous_dj.generated.persistent_memory import PersistentMemory

memory = PersistentMemory()
memory.initialize()  # Creates data/memory/chroma_db/
```


### 6. Module Import Errors

#### Symptom
```
ImportError: cannot import name 'play_deck' from 'autonomous_dj.generated.deck_operations'
```

#### Root Cause
Generated modules missing or incomplete

#### Solution
1. Check if module exists:
```bash
ls autonomous_dj/generated/deck_operations.py
```

2. If missing, regenerate using appropriate agent:
```
Use deck-control-specialist agent to regenerate deck_operations.py module
```

3. If exists but incomplete, review and patch module

### 7. High Latency / Delayed Response

#### Symptom
MIDI commands take >100ms to execute, noticeable delay

#### Possible Causes & Solutions

**A. WASAPI Audio Driver**
See Issue #1 - Switch to ASIO

**B. System Overload**
```bash
# Check CPU usage
Task Manager → Performance → CPU

# Close unnecessary applications
# Reduce buffer size in ASIO settings (with caution)
```

**C. Python GIL Contention**
```python
# Use subprocess for MIDI commands instead of threading
import subprocess

def send_midi_command(cc, value):
    subprocess.run(['python', 'send_midi.py', str(cc), str(value)])
```

### 8. Autonomous Loop Not Triggering

#### Symptom
Autonomous mode enabled but no automatic track loading

#### Debug Steps

1. Check timing detection:
```python
from autonomous_dj.generated.timing_analyzer import get_bars_remaining

bars = get_bars_remaining('A')
print(f"Bars remaining: {bars}")
# Should trigger at <32 bars
```

2. Check LLM integration:
```python
from autonomous_dj.generated.llm_integration import LLMIntegration

llm = LLMIntegration()
status = await llm.health_check()
print(f"LLM Status: {status}")
```

3. Review logs:
```bash
cat data/llm_logs.json
# Check for errors or API rate limits
```


### 6. Module Import Errors

#### Symptom
```
ImportError: cannot import name 'play_deck' from 'autonomous_dj.generated.deck_operations'
```

#### Root Cause
Generated modules missing or incomplete

#### Solution
1. Check if module exists:
```bash
ls autonomous_dj/generated/deck_operations.py
```

2. If missing, regenerate using appropriate agent:
```
Use deck-control-specialist agent to regenerate deck_operations.py module
```

3. If exists but incomplete, review and patch module

### 7. High Latency / Delayed Response

#### Symptom
MIDI commands take >100ms to execute, noticeable delay

#### Possible Causes & Solutions

**A. WASAPI Audio Driver**
See Issue #1 - Switch to ASIO

**B. System Overload**
```bash
# Check CPU usage
Task Manager → Performance → CPU

# Close unnecessary applications
# Reduce buffer size in ASIO settings (with caution)
```

**C. Python GIL Contention**
```python
# Use subprocess for MIDI commands instead of threading
import subprocess

def send_midi_command(cc, value):
    subprocess.run(['python', 'send_midi.py', str(cc), str(value)])
```

### 8. Autonomous Loop Not Triggering

#### Symptom
Autonomous mode enabled but no automatic track loading

#### Debug Steps

1. Check timing detection:
```python
from autonomous_dj.generated.timing_analyzer import get_bars_remaining

bars = get_bars_remaining('A')
print(f"Bars remaining: {bars}")
# Should trigger at <32 bars
```

2. Check LLM integration:
```python
from autonomous_dj.generated.llm_integration import LLMIntegration

llm = LLMIntegration()
status = await llm.health_check()
print(f"LLM Status: {status}")
```

3. Review logs:
```bash
cat data/llm_logs.json
# Check for errors or API rate limits
```


### 6. Module Import Errors

#### Symptom
```
ImportError: cannot import name 'play_deck' from 'autonomous_dj.generated.deck_operations'
```

#### Root Cause
Generated modules missing or incomplete

#### Solution
1. Check if module exists:
```bash
ls autonomous_dj/generated/deck_operations.py
```

2. If missing, regenerate using appropriate agent:
```
Use deck-control-specialist agent to regenerate deck_operations.py module
```

3. If exists but incomplete, review and patch module

### 7. High Latency / Delayed Response

#### Symptom
MIDI commands take >100ms to execute, noticeable delay

#### Possible Causes & Solutions

**A. WASAPI Audio Driver**
See Issue #1 - Switch to ASIO

**B. System Overload**
```bash
# Check CPU usage
Task Manager → Performance → CPU

# Close unnecessary applications
# Reduce buffer size in ASIO settings (with caution)
```

**C. Python GIL Contention**
```python
# Use subprocess for MIDI commands instead of threading
import subprocess

def send_midi_command(cc, value):
    subprocess.run(['python', 'send_midi.py', str(cc), str(value)])
```

### 8. Autonomous Loop Not Triggering

#### Symptom
Autonomous mode enabled but no automatic track loading

#### Debug Steps

1. Check timing detection:
```python
from autonomous_dj.generated.timing_analyzer import get_bars_remaining

bars = get_bars_remaining('A')
print(f"Bars remaining: {bars}")
# Should trigger at <32 bars
```

2. Check LLM integration:
```python
from autonomous_dj.generated.llm_integration import LLMIntegration

llm = LLMIntegration()
status = await llm.health_check()
print(f"LLM Status: {status}")
```

3. Review logs:
```bash
cat data/llm_logs.json
# Check for errors or API rate limits
```

