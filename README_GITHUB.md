# Traktor AI - Autonomous DJ System

Sistema DJ autonomo con AI vision-guided per Traktor Pro 3.

## Features

- **Multi-Screen Vision Capture**: Cattura automaticamente tutti gli schermi
- **Claude Vision AI Analysis**: Analisi intelligente dell'interfaccia Traktor
- **MIDI Control**: Driver MIDI completo con 100+ CC mappings
- **Safety Layer**: Protezione contro operazioni dannose
- **Track Matching**: Algoritmo di matching intelligente per selezione tracce
- **Autonomous Workflow**: Workflow completo caricamento/play/sync/mix

## Quick Start

### Prerequisites

1. **Traktor Pro 3** installed and running
2. **loopMIDI** configured with "Traktor MIDI Bus 1"
3. **ASIO driver** (NOT WASAPI - blocks MIDI!)
4. **MIDI Interaction Mode = "Direct"** in Traktor Controller Manager
5. Python 3.8+

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/traktor.git
cd traktor
```

### 2. Setup API Keys ⚠️ IMPORTANTE

```bash
# Copy config template
cp autonomous_dj/config.template.py autonomous_dj/config.py

# Edit config.py and add your API keys:
# - ANTHROPIC_API_KEY (from console.anthropic.com)
# - OPENROUTER_API_KEY (optional, from openrouter.ai)
```

**⚠️ NEVER commit config.py - it's in .gitignore!**

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

On Windows with system Python:
```bash
pip install -r requirements.txt --break-system-packages
```

### 4. Verify MIDI Setup

```bash
python verify_midi_setup.py
```

Expected output:
```
✓ loopMIDI virtual port found
✓ Traktor MIDI Bus 1 available
✓ MIDI driver initialized
```

### 5. Test Vision System

```bash
# Test basic vision capture
python test_basic_vision.py

# Test Claude Vision AI
python test_claude_vision.py

# Test MIDI only
python test_midi_only.py
```

## Project Structure

```
traktor/
├── autonomous_dj/              # Core backend
│   ├── config.py               # ⚠️ NOT IN GIT (your API keys)
│   ├── config.template.py      # Template (safe to commit)
│   ├── traktor_vision.py       # Vision capture system
│   ├── claude_vision_client.py # Claude AI integration
│   ├── traktor_midi_driver.py  # MIDI driver
│   ├── traktor_safety_checks.py # Safety layer
│   └── workflow_controller.py  # Autonomous workflow
│
├── data/                       # Runtime data (not in git)
│   ├── screenshots/            # Vision screenshots
│   ├── backups/                # Traktor collection backups
│   └── logs/                   # Application logs
│
├── config/                     # Configuration files
│   ├── traktor_midi_mapping.json
│   └── keyboard_shortcuts_mapping.json
│
├── .gitignore                  # ⚠️ Protects API keys
├── requirements.txt            # Python dependencies
└── CLAUDE.md                   # Complete documentation
```

## Configuration

### API Keys (Required)

Edit `autonomous_dj/config.py`:

```python
# Anthropic API (required for vision)
ANTHROPIC_API_KEY = "sk-ant-api03-..."

# OpenRouter API (optional)
OPENROUTER_API_KEY = "sk-or-v1-..."
```

Get keys:
- Anthropic: https://console.anthropic.com/settings/keys
- OpenRouter: https://openrouter.ai/keys

## Security

**API keys are NEVER committed to git.**

Protected files (in .gitignore):
- `autonomous_dj/config.py` (contains API keys)
- `.env` files
- `data/screenshots/` (may contain personal info)
- `data/backups/` (Traktor collection)
- `data/logs/` (application logs)

## Documentation

- **CLAUDE.md**: Complete project overview and setup
- **DJ_WORKFLOW_RULES.md**: Professional DJ workflow rules

## License

Private - All Rights Reserved

## Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com) - AI vision analysis
- [Traktor Pro 3](https://www.native-instruments.com/traktor) - DJ software
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html) - Virtual MIDI

---

**For detailed documentation, see CLAUDE.md**
