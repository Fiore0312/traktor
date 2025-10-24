# Traktor DJ Autonomous System

🎛️ **Autonomous DJ system** controlling Traktor Pro 3 via MIDI for professional music mixing.

## Quick Start

### Prerequisites
- Traktor Pro 3 running
- loopMIDI with "Traktor MIDI Bus 1"
- ASIO audio driver (NOT WASAPI!)
- Python 3.8+

### Setup
```bash
# 1. Crea/attiva virtual environment (automatico in VS Code!)
cd C:\traktor
code .  # VS Code attiverà il venv automaticamente

# 2. Installa dipendenze (nel terminale VS Code)
pip install -r requirements.txt

# 3. Verifica MIDI
python verify_midi_setup.py
```

**Nota**: Il virtual environment è già configurato e si attiverà automaticamente quando apri il terminale in VS Code. Vedi `VSCODE_SETUP.md` per dettagli.

### Usage with Claude Code
```bash
cd C:\traktor
claude
# Claude Code si aprirà e caricherà automaticamente il contesto
# Chiedi: "Carica una traccia sul Deck A"
```

**Oppure con VS Code normale**:
```bash
code .
```

## Documentation

- **`claude.md`** - Project guide for Claude Code
- **`.claude/skills/traktor-dj-autonomous/SKILL.md`** - Complete system documentation
- **`DJ_WORKFLOW_RULES.md`** - Professional DJ workflow rules
- **`MIGRATION_NOTES.md`** - Migration details from djfiore

## Architecture

**Skill-based system** using:
- MIDI communication (<10ms latency)
- 18 production-ready modules
- Configuration-driven design
- Professional DJ workflow compliance

## Key Features

✅ Real-time MIDI control of Traktor Pro 3  
✅ **Vision-guided navigation** - Claude "sees" Traktor UI  
✅ Intelligent track selection with LLM integration  
✅ Automated mixing with phrase-perfect timing  
✅ Energy flow analysis  
✅ Screenshot-based state verification  
✅ Persistent memory system (ChromaDB)

## Project Structure

```
traktor/
├── .claude/skills/traktor-dj-autonomous/  # Skill documentation
├── autonomous_dj/                          # Core system
│   └── generated/                          # 18 production modules
├── config/                                 # Configuration files
├── traktor_midi_driver.py                  # MIDI driver
└── DJ_WORKFLOW_RULES.md                    # Workflow rules
```

## Development

Read **`.claude/skills/traktor-dj-autonomous/SKILL.md`** first!

All development should follow:
1. Configuration-driven approach (no hardcoded values)
2. DJ workflow rules compliance
3. Modular architecture patterns
4. MIDI-first control strategy

---

**For detailed documentation, see `.claude/skills/traktor-dj-autonomous/SKILL.md`**
