# Traktor DJ Autonomous System

## Project Overview

This is an **autonomous DJ system** that controls Traktor Pro 3 via **MIDI** for professional music mixing and performance.

**Architecture**: Skill-based system using Claude's `.claude/skills/` framework.

## Critical Files to Read First

1. **`.claude/skills/traktor-dj-autonomous/SKILL.md`** - Complete system documentation (READ THIS FIRST!)
2. **`DJ_WORKFLOW_RULES.md`** - Professional DJ workflow rules (CRITICAL!)
3. **`traktor_midi_driver.py`** - MIDI communication driver (100+ CC mappings)
4. **`config/traktor_midi_mapping.json`** - CC mapping configuration

## Quick Start

### Prerequisites
1. **Traktor Pro 3** must be running
2. **loopMIDI** configured with "Traktor MIDI Bus 1"
3. **ASIO driver** (NOT WASAPI - WASAPI blocks MIDI!)
4. **MIDI Interaction Mode = "Direct"** (CRITICAL! See MIDI_INTERACTION_MODE_FIX.md)
5. Python 3.8+ with dependencies installed
6. **IMPORTANT: Multi-Screen Setup**
   - ⚠️ **CRITICAL**: Traktor can be on **PRIMARY or SECONDARY screen**
   - Vision system auto-captures ALL screens automatically
   - No configuration needed - works regardless of monitor setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Verify MIDI Setup
```bash
python verify_midi_setup.py
```

## 🎧 Vision-Guided Autonomous Workflow (NEW!)

**Complete autonomous DJ system with AI vision analysis!**

### Quick Test (Safe Mode)
```bash
# Double-click on file:
RUN_VISION_TEST.bat

# Or from command line:
.\venv\Scripts\python.exe test_vision_simple.py
```

### Single Iteration (Live Mode)
```bash
# Execute ONE complete cycle with REAL MIDI:
RUN_VISION_WORKFLOW_SINGLE.bat
```

### Full Autonomous Loop
```bash
# Infinite loop - full DJ automation:
RUN_VISION_WORKFLOW_LOOP.bat
# Press Ctrl+C to stop
```

**Documentation**: See `README_VISION_WORKFLOW.md` for complete guide.

**Features**:
- ✅ Claude Vision API (real-time UI analysis)
- ✅ Safety Layer integration
- ✅ MIDI Driver (real-time control)
- ✅ Intelligent decision making
- ✅ Autonomous load/play/sync workflow

## Project Structure

```
traktor/
├── .claude/
│   └── skills/
│       └── traktor-dj-autonomous/
│           ├── SKILL.md              # Complete system documentation
│           ├── references/           # Additional docs (CC mappings, troubleshooting)
│           └── scripts/              # Utility scripts
│
├── autonomous_dj/                    # Core system
│   ├── generated/                    # 18 production-ready modules
│   │   ├── deck_operations.py        # Deck control with MASTER/SYNC logic
│   │   ├── mixer_operations.py       # Volume, crossfader, EQ
│   │   ├── transport_operations.py   # Sync, tempo, beatmatching
│   │   ├── loop_operations.py        # Beat-perfect loops
│   │   ├── hotcue_operations.py      # 32-HOTCUE system
│   │   ├── fx_operations.py          # Effects control
│   │   ├── mix_executor.py           # Automated transitions
│   │   ├── timing_analyzer.py        # Phrase detection
│   │   ├── energy_analyzer.py        # Energy flow analysis
│   │   ├── track_selector.py         # Intelligent track selection
│   │   ├── track_metadata.py         # Metadata extraction
│   │   ├── browser_navigator.py      # MIDI browser navigation
│   │   ├── llm_integration.py        # OpenRouter + LangChain
│   │   ├── persistent_memory.py      # ChromaDB knowledge base
│   │   └── ... (14 more modules)
│   │
│   ├── live_performer.py             # Main event loop (500ms)
│   ├── background_intelligence.py    # Strategy layer
│   └── state_manager.py              # State coordination
│
├── config/
│   ├── traktor_midi_mapping.json     # CC mappings (source of truth)
│   ├── config_loader.py              # Configuration loader
│   └── keyboard_shortcuts_mapping.json
│
├── data/                              # Runtime data
│   ├── state.json                     # Current system state
│   └── memory/                        # Persistent knowledge (ChromaDB)
│
├── traktor_midi_driver.py             # MIDI communication (<10ms latency)
├── DJ_WORKFLOW_RULES.md               # Professional workflow rules
├── requirements.txt                   # Python dependencies
└── verify_midi_setup.py               # MIDI verification script
```

## How to Use This Project

### With Claude Code (Recommended)

Claude Code will automatically:
1. Read this `claude.md` file for project context
2. Load the `.claude/skills/traktor-dj-autonomous/SKILL.md` when needed
3. Use the skill's knowledge to help you work on the project

**Just ask Claude Code what you need!** Examples:
- "Load a Techno track on Deck A"
- "Start mixing Deck A and Deck B"
- "Check MIDI connection status"
- "Explain the MASTER/SYNC workflow"

### Key Concepts

**1. MIDI Control is Primary**
- All Traktor control happens via MIDI CC messages
- loopMIDI creates virtual MIDI bus: "Traktor MIDI Bus 1"
- <10ms latency for real-time performance

**2. Configuration-Driven**
- NEVER hardcode CC values
- ALWAYS use `config/traktor_midi_mapping.json`
- Use `config_loader.py` to access configurations

**3. DJ Workflow Compliance**
- Follow rules in `DJ_WORKFLOW_RULES.md`
- MASTER vs SYNC logic is critical
- AUTO mode handles MASTER transfers automatically
- Pre-playback mixer setup is mandatory

**4. Modular Architecture**
- Each module in `autonomous_dj/generated/` is production-ready
- Modules are PERMANENT (no regeneration unless bugfix needed)
- One module = one responsibility

## Critical Rules

### MASTER vs SYNC Decision (with AUTO mode)

**First track (no other playing)**:
- ✅ Set as MASTER (manual)
- ❌ Do NOT enable SYNC (nothing to sync to)
- ✅ High volume fader (~85%)

**Second+ track (deck already playing)**:
- ❌ Do NOT manually set MASTER (AUTO handles it)
- ✅ Enable SYNC (matches BPM automatically)
- ✅ Start with LOW volume (0-20%)
- ✅ During transition: volume up → AUTO transfers MASTER

### Pre-Playback Mixer Setup

ALWAYS configure mixer BEFORE pressing play:
1. Position crossfader (A → LEFT, B → RIGHT)
2. Volume faders ready (playing: 85%, incoming: 0-20%)
3. EQ neutral (12 o'clock)
4. THEN press play

## Common Tasks

### Test MIDI Connection
```bash
python verify_midi_setup.py
```

### Play First Track
```python
from autonomous_dj.generated import deck_operations

deck_operations.initialize_deck_operations()
result = deck_operations.play_deck('A', first_track=True)
print(result)
```

### Load and Mix Two Tracks
```python
from autonomous_dj import live_performer

# This will handle the complete workflow
live_performer.start_autonomous_session()
```

## Troubleshooting

### MIDI Not Working
1. Check Traktor's Audio Device setting
2. Must be **ASIO** (NOT WASAPI)
3. WASAPI blocks MIDI processing
4. Install ASIO4ALL if no native ASIO driver
5. **CHECK INTERACTION MODE**: Must be "Direct" (not Toggle/Hold)
   - Go to Preferences → Controller Manager
   - Select Generic MIDI device
   - For each control, set Interaction Mode = "Direct"
   - See `MIDI_INTERACTION_MODE_FIX.md` for details

### Browser Navigation Too Fast
- Traktor requires 1.5-2s delay between commands
- Commands <1s are ignored

### For More Help
- Read `.claude/skills/traktor-dj-autonomous/SKILL.md`
- Check `references/troubleshooting.md` in skill folder
- Review `DJ_WORKFLOW_RULES.md` for workflow issues

## Development Guidelines

### Adding New Features
1. Create code in `autonomous_dj/generated/`
2. Follow existing module patterns
3. Use `config_loader` for all configurations
4. Test with real Traktor before deploying
5. Document in skill's SKILL.md

### Testing Strategy
- Manual testing with Traktor required
- Verify MIDI latency stays <10ms
- Follow DJ workflow rules
- Test transitions thoroughly

## Migration Notes

This project was migrated from `C:\djfiore` with the following improvements:
- ✅ Skill-based architecture (no more problematic sub-agents)
- ✅ Clean configuration management
- ✅ All 18 production modules preserved
- ✅ MIDI driver verified and working
- ✅ Professional DJ workflow compliance built-in

**Previous issues RESOLVED:**
- ❌ Sub-agents losing instructions → ✅ Skill-based system maintains context
- ❌ Screenshot-based navigation issues → ✅ MIDI browser navigation
- ❌ Workflow violations → ✅ Rules enforced in SKILL.md

## Next Steps

1. **Verify environment**: Run `python verify_midi_setup.py`
2. **Read the skill**: Open `.claude/skills/traktor-dj-autonomous/SKILL.md`
3. **Test basic operations**: Load a track, adjust volume, test sync
4. **Start development**: Use Claude Code to add features or fix issues

---

**For detailed documentation, ALWAYS refer to `.claude/skills/traktor-dj-autonomous/SKILL.md`**
