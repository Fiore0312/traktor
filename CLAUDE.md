# Traktor AI - Autonomous DJ System

**Last Updated:** October 25, 2025
**Project Status:** Core Backend Complete - Ready for Full-Stack Development
**Repository:** https://github.com/Fiore0312/traktor

---

## 📋 PROJECT OVERVIEW

Autonomous DJ system for Traktor Pro 3 with **AI-powered vision analysis**, **MIDI control**, and **intelligent track selection**.

**Goal:** Create a conversational interface (like Claude.ai) to control Traktor autonomously through natural language commands.

**Current Status:**
- ✅ Backend core complete (vision, MIDI, safety, workflow)
- ✅ GitHub repository created with protected API keys
- ✅ Multi-screen vision capture working
- ✅ Claude Vision AI integration complete
- ✅ Safety layer implemented
- ✅ Track matching algorithm prepared
- 🔄 Next: Full-stack application (API server + web UI)

**Architecture**: Vision-guided system with Claude AI integration and real-time MIDI control.

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│              DJ AI APPLICATION                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend (Web UI) [PLANNED]                            │
│  ├─ Chat Interface (user commands)                      │
│  ├─ Real-time Traktor Status Display                   │
│  └─ Mode Selector (Manual/Assisted/Autonomous)         │
│                                                         │
│  API Server (FastAPI) [PLANNED]                         │
│  ├─ REST endpoints (/api/command, /api/status)         │
│  ├─ WebSocket (real-time updates)                      │
│  └─ Workflow orchestration                             │
│                                                         │
│  Backend Components [IMPLEMENTED ✅]                    │
│  ├─ Workflow Controller (command processor)            │
│  ├─ Vision System (multi-screen screenshot)            │
│  ├─ Claude Vision AI (UI analysis)                     │
│  ├─ MIDI Driver (Traktor control)                      │
│  ├─ Safety Checks (DJ best practices)                  │
│  ├─ Track Matcher (compatibility algorithm)            │
│  └─ Collection Parser (Traktor database)               │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │
         ↓ MIDI Control (loopMIDI)

    Traktor Pro 3
```

---

## 🚀 QUICK START

### 1. Clone Repository

```bash
git clone https://github.com/Fiore0312/traktor.git
cd traktor
```

### 2. Setup API Keys ⚠️ CRITICAL

```bash
# Copy config template
cp autonomous_dj/config.template.py autonomous_dj/config.py

# Edit config.py and add your API keys:
# - ANTHROPIC_API_KEY (from https://console.anthropic.com/settings/keys)
# - OPENROUTER_API_KEY (optional, from https://openrouter.ai/keys)
```

**⚠️ NEVER commit config.py - it's protected by .gitignore!**

### 3. Prerequisites

1. **Traktor Pro 3** must be running
2. **loopMIDI** configured with "Traktor MIDI Bus 1"
3. **ASIO driver** (NOT WASAPI - WASAPI blocks MIDI!)
4. **MIDI Interaction Mode = "Direct"** (CRITICAL! See MIDI_INTERACTION_MODE_FIX.md)
5. Python 3.8+ with dependencies installed
6. **IMPORTANT: Multi-Screen Setup**
   - ⚠️ **CRITICAL**: Traktor can be on **PRIMARY or SECONDARY screen**
   - Vision system auto-captures ALL screens automatically
   - No configuration needed - works regardless of monitor setup

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

On Windows with system Python:
```bash
pip install -r requirements.txt --break-system-packages
```

### 5. Verify MIDI Setup

```bash
python verify_midi_setup.py
```

Expected output:
```
✓ loopMIDI virtual port found
✓ Traktor MIDI Bus 1 available
✓ MIDI driver initialized
```

### 6. Test Vision System

```bash
# Test basic vision capture
python test_basic_vision.py

# Test Claude Vision AI
python test_claude_vision.py

# Test MIDI only
python test_midi_only.py
```

---

## 🎧 VISION-GUIDED AUTONOMOUS WORKFLOW

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

---

## 📁 PROJECT STRUCTURE

```
traktor/
├── .github/                           # GitHub configuration (future)
│
├── .claude/
│   └── skills/
│       └── traktor-dj-autonomous/
│           ├── SKILL.md               # Complete system documentation
│           ├── references/            # Additional docs
│           └── scripts/               # Utility scripts
│
├── autonomous_dj/                     # Core system
│   ├── config.py                      # ⚠️ NOT IN GIT (your API keys)
│   ├── config.template.py             # Template (safe to commit)
│   │
│   ├── traktor_vision.py              # Vision capture system
│   ├── claude_vision_client.py        # Claude AI integration
│   ├── workflow_controller.py         # Autonomous workflow
│   ├── track_matcher.py               # Track selection AI
│   │
│   └── generated/                     # 18 production-ready modules
│       ├── deck_operations.py         # Deck control
│       ├── mixer_operations.py        # Volume, crossfader, EQ
│       ├── transport_operations.py    # Sync, tempo, beatmatching
│       ├── loop_operations.py         # Beat-perfect loops
│       ├── hotcue_operations.py       # 32-HOTCUE system
│       ├── fx_operations.py           # Effects control
│       ├── mix_executor.py            # Automated transitions
│       ├── timing_analyzer.py         # Phrase detection
│       ├── energy_analyzer.py         # Energy flow analysis
│       ├── track_selector.py          # Intelligent track selection
│       ├── track_metadata.py          # Metadata extraction
│       ├── browser_navigator.py       # MIDI browser navigation
│       ├── llm_integration.py         # OpenRouter + LangChain
│       ├── persistent_memory.py       # ChromaDB knowledge base
│       └── ... (14 more modules)
│
├── config/
│   ├── traktor_midi_mapping.json      # CC mappings (source of truth)
│   ├── config_loader.py               # Configuration loader
│   └── keyboard_shortcuts_mapping.json
│
├── data/                               # Runtime data (NOT IN GIT)
│   ├── screenshots/                    # Vision screenshots
│   ├── backups/                        # Traktor collection backups
│   ├── logs/                           # Application logs
│   └── memory/                         # Persistent knowledge (ChromaDB)
│
├── traktor_midi_driver.py              # MIDI communication
├── traktor_safety_checks.py            # Safety rules validation
├── DJ_WORKFLOW_RULES.md                # Professional workflow rules
├── CLAUDE.md                           # This file
├── README.md                           # GitHub README
├── requirements.txt                    # Python dependencies
├── .gitignore                          # ⚠️ Protects API keys
└── verify_midi_setup.py                # MIDI verification script
```

---

## 🔑 CONFIGURATION & API KEYS

### Initial Setup

After cloning, you MUST create `autonomous_dj/config.py`:

```bash
cp autonomous_dj/config.template.py autonomous_dj/config.py
```

Edit `config.py` and add:

```python
# Anthropic API (required for vision)
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-KEY-HERE"

# OpenRouter API (optional)
OPENROUTER_API_KEY = "sk-or-v1-YOUR-KEY-HERE"
```

### Get API Keys

- **Anthropic**: https://console.anthropic.com/settings/keys
- **OpenRouter**: https://openrouter.ai/keys

### Security

**config.py is in .gitignore and will NEVER be committed!**

Files protected from git:
- `autonomous_dj/config.py` (contains real API keys)
- `.env` (environment variables)
- `data/screenshots/` (may contain personal info)
- `data/backups/` (Traktor collection)
- `data/logs/` (application logs)

---

## 🎛️ HOW TO USE THIS PROJECT

### With Claude Code (Recommended)

Claude Code will automatically:
1. Read this `CLAUDE.md` file for project context
2. Load the `.claude/skills/traktor-dj-autonomous/SKILL.md` when needed
3. Use the skill's knowledge to help you work on the project

**Just ask Claude Code what you need!** Examples:
- "Load a Techno track on Deck A"
- "Start mixing Deck A and Deck B"
- "Check MIDI connection status"
- "Explain the MASTER/SYNC workflow"
- "Test the vision system"

---

## 🧠 KEY CONCEPTS

### 1. MIDI Control is Primary

- All Traktor control happens via MIDI CC messages
- loopMIDI creates virtual MIDI bus: "Traktor MIDI Bus 1"
- <10ms latency for real-time performance
- 100+ CC mappings for complete control

### 2. Configuration-Driven

- NEVER hardcode CC values
- ALWAYS use `config/traktor_midi_mapping.json`
- Use `config_loader.py` to access configurations

### 3. DJ Workflow Compliance

- Follow rules in `DJ_WORKFLOW_RULES.md`
- MASTER vs SYNC logic is critical
- AUTO mode handles MASTER transfers automatically

### 4. Vision-Guided Control

- Multi-screen capture (works on any monitor)
- Claude Vision AI analyzes Traktor UI
- Real-time state detection

### 5. Safety Layer

- Validates all operations before execution
- Prevents dangerous mixer states
- Enforces DJ best practices

---

## ⚠️ CRITICAL RULES

### MASTER vs SYNC Decision

**First track (no other playing)**:
- ✅ Set as MASTER (manual)
- ❌ Do NOT enable SYNC (nothing to sync to)
- ✅ High volume fader (~85%)

**Second+ track (deck already playing)**:
- ❌ Do NOT manually set MASTER (AUTO handles it)
- ✅ Enable SYNC (matches BPM automatically)
- ✅ Start with LOW volume (0-20%)

### Pre-Playback Mixer Setup

ALWAYS configure mixer BEFORE pressing play:
1. Position crossfader
2. Volume faders ready
3. EQ neutral
4. THEN press play

---

## 🐛 TROUBLESHOOTING

### MIDI Not Working

1. **Check Audio Device**: Must be ASIO (NOT WASAPI)
2. **Verify loopMIDI**: "Traktor MIDI Bus 1" must exist
3. **Check Interaction Mode**: Must be "Direct"
4. Run `python verify_midi_setup.py`

See: `MIDI_INTERACTION_MODE_FIX.md`

### Vision Not Working

1. Verify Anthropic API key in `autonomous_dj/config.py`
2. Check screenshot directory exists
3. Run `python test_basic_vision.py`

---

## 🗺️ ROADMAP & NEXT STEPS

### Phase 1: Core Backend ✅ COMPLETE

- [x] MIDI driver implementation
- [x] Vision system (multi-screen capture)
- [x] Claude Vision AI integration
- [x] Safety layer
- [x] Track matching algorithm
- [x] Workflow controller
- [x] GitHub repository setup

### Phase 2: Full-Stack Application 🔄 IN PROGRESS

- [ ] FastAPI server
- [ ] Web Frontend (chat interface)
- [ ] Real-time status display
- [ ] WebSocket for updates

### Phase 3: Intelligence & Automation

- [ ] Track selection AI
- [ ] Energy flow analysis
- [ ] Phrase-aware mixing
- [ ] Persistent memory

---

## 📚 DOCUMENTATION

### Essential Reading

1. **CLAUDE.md** (this file) - Project overview
2. **`.claude/skills/traktor-dj-autonomous/SKILL.md`** - Complete system documentation
3. **`DJ_WORKFLOW_RULES.md`** - Professional workflow rules
4. **`README_VISION_WORKFLOW.md`** - Vision system guide
5. **`MIDI_INTERACTION_MODE_FIX.md`** - Critical MIDI setup

---

**For detailed technical documentation, ALWAYS refer to `.claude/skills/traktor-dj-autonomous/SKILL.md`**

**Last Updated:** October 25, 2025
