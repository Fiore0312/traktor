# DJ AI - Full-Stack Application Guide

**Last Updated:** October 25, 2025

---

## 📋 OVERVIEW

Applicazione completa full-stack per controllare Traktor Pro 3 con interfaccia conversazionale stile Claude.ai.

**Stack:**
- **Backend:** Python + FastAPI + WebSocket
- **Frontend:** HTML + CSS (Dark Mode) + JavaScript
- **AI Vision:** Claude Vision API (Anthropic)
- **AI Chat:** LLM gratuito via OpenRouter (opzionale)
- **MIDI:** Real-time control via loopMIDI

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│              DJ AI APPLICATION                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend (Web UI) [✅ COMPLETE]                        │
│  ├─ Chat Interface (Claude.ai style)                    │
│  ├─ Real-time Traktor Status Display                   │
│  ├─ Mode Selector (Manual/Assisted/Autonomous)         │
│  └─ Quick Actions Sidebar                              │
│                                                         │
│  API Server (FastAPI) [✅ COMPLETE]                     │
│  ├─ REST endpoints (/api/command, /api/status)         │
│  ├─ WebSocket (real-time updates every 2s)             │
│  └─ Health check endpoint                              │
│                                                         │
│  Backend Components [✅ READY]                          │
│  ├─ Workflow Controller (command processor)            │
│  ├─ Vision System (multi-screen screenshot)            │
│  ├─ Claude Vision AI (UI analysis)                     │
│  ├─ MIDI Driver (Traktor control)                      │
│  ├─ Safety Checks (DJ best practices)                  │
│  └─ Track Matcher (compatibility algorithm)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 QUICK START

### Option 1: Demo Mode (No Configuration Required)

Per testare subito l'interfaccia senza configurare Traktor:

```bash
# Double-click su:
START_SERVER_DEMO.bat

# O da command line:
cd C:\traktor
python -m uvicorn server_demo:app --host 0.0.0.0 --port 8000 --reload
```

Poi apri: **http://localhost:8000**

**Demo Mode Features:**
- ✅ Full UI funzionante
- ✅ WebSocket real-time updates
- ✅ Comandi simulati
- ❌ No Traktor integration
- ❌ No AI vision analysis

---

### Option 2: Full Production Mode

Per usare l'applicazione completa con Traktor:

#### 1. Prerequisites

- ✅ Traktor Pro 3 running
- ✅ loopMIDI configured ("Traktor MIDI Bus 1")
- ✅ ASIO driver (NOT WASAPI)
- ✅ MIDI Interaction Mode = "Direct"
- ✅ API Keys configured

#### 2. Configure API Keys

```bash
# Copy template
cp autonomous_dj/config.template.py autonomous_dj/config.py

# Edit autonomous_dj/config.py and add:
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-KEY-HERE"  # Required
OPENROUTER_API_KEY = "sk-or-v1-YOUR-KEY-HERE"     # Optional
```

Get keys:
- **Anthropic**: https://console.anthropic.com/settings/keys
- **OpenRouter**: https://openrouter.ai/keys (gratis)

#### 3. Start Production Server

```bash
cd C:\traktor
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Poi apri: **http://localhost:8000**

---

## 🎨 INTERFACE OVERVIEW

### Main Layout (Claude.ai Style)

```
┌──────────────┬────────────────────────────────────────┐
│              │                                        │
│   SIDEBAR    │         CHAT AREA                     │
│              │                                        │
│  - Logo      │  [Chat messages]                      │
│  - Modes     │                                        │
│  - Status    │  [User/Assistant conversation]        │
│  - Actions   │                                        │
│              │                                        │
│              │  [Input box with send button]         │
│              │                                        │
└──────────────┴────────────────────────────────────────┘
```

### Sidebar Components

**1. Mode Selector:**
- **Manual**: Controllo manuale via comandi
- **Assisted**: AI suggerisce, user approva
- **Autonomous**: AI gestisce tutto automaticamente

**2. Traktor Status** (Real-time):
- Browser: Current track highlighted
- Deck A: Status, Track, Playing state
- Deck B: Status, Track, Playing state
- Connection indicator (green = connected)

**3. Quick Actions:**
- 📊 Show Status
- ⬇️ Load Track A/B
- ▶️ Play Deck A/B

### Chat Interface

**Stile identico a Claude.ai:**
- Dark mode colors (#1A1A1A background)
- Message bubbles con avatar
- Syntax highlighting per codice
- Auto-scroll al nuovo messaggio
- Input con supporto multi-line (Shift+Enter)

---

## 💬 COMMAND EXAMPLES

### Basic Commands

```
"Mostrami lo stato"
"Show me the current status"

"Carica una traccia su Deck A"
"Load a Techno track on Deck B"

"Fai play su Deck A"
"Play Deck B"

"Ferma Deck A"
"Pause Deck B"
```

### Advanced Commands

```
"Carica una traccia Dub su Deck A"
"Load a Dub track on Deck A and start playing"

"Avvia modalità autonoma"
"Start autonomous mixing"

"Fai un mix tra Deck A e B"
"Mix Deck A and B with smooth transition"
```

---

## 🔧 API ENDPOINTS

### REST API

```
GET  /                      → Frontend HTML
GET  /api/health            → Health check
GET  /api/status            → Current Traktor state
POST /api/command           → Execute user command
     Body: {"command": "..."}
```

### WebSocket

```
WS /ws                      → Real-time state updates (every 2s)
```

### Example API Call

```bash
# Health check
curl http://localhost:8000/api/health

# Get status
curl http://localhost:8000/api/status

# Send command
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Mostrami lo stato"}'
```

---

## 📁 FILE STRUCTURE

```
traktor/
├── server.py                    # Production server (with Traktor)
├── server_demo.py               # Demo server (standalone)
├── START_SERVER_DEMO.bat        # Quick start script
│
├── autonomous_dj/
│   ├── workflow_controller.py   # Main orchestrator
│   ├── claude_vision_client.py  # Vision AI
│   ├── config.py                # ⚠️ NOT IN GIT (your API keys)
│   └── config.template.py       # Safe template
│
├── frontend/
│   ├── index.html               # Main UI (Claude.ai style)
│   ├── style.css                # Dark mode styling
│   └── app.js                   # WebSocket + API logic
│
├── traktor_midi_driver.py       # MIDI control
├── traktor_safety_checks.py     # Safety layer
│
└── README_FULLSTACK_APP.md      # This file
```

---

## 🎨 STYLING (Claude.ai Dark Mode)

### Color Palette

```css
--color-bg-primary: #1A1A1A;      /* Main background */
--color-bg-secondary: #2A2A2A;    /* Cards */
--color-sidebar: #1F1F1F;         /* Sidebar */

--color-text-primary: #ECECEC;    /* Main text */
--color-text-secondary: #B4B4B4;  /* Secondary text */

--color-accent: #CC785C;          /* Accent (buttons, links) */
--color-border: #3A3A3A;          /* Borders */
```

### Fonts

- **Sans**: -apple-system, Segoe UI, Roboto, Arial
- **Mono**: SF Mono, Monaco, Inconsolata

---

## 🔌 WEBSOCKET PROTOCOL

### Client → Server

Connessione iniziale:
```javascript
ws = new WebSocket('ws://localhost:8000/ws');
```

### Server → Client (Every 2s)

```json
{
  "browser": {
    "track_highlighted": "Track Name.mp3"
  },
  "deck_a": {
    "status": "loaded",
    "track_title": "Artist - Track",
    "playing": true
  },
  "deck_b": {
    "status": "empty",
    "track_title": "",
    "playing": false
  },
  "mixer": {},
  "mode": "manual",
  "last_update": 1729818260.5
}
```

---

## 🐛 TROUBLESHOOTING

### Server won't start

```
Error: Cannot import workflow_controller
Solution: Use server_demo.py for testing UI
```

### WebSocket disconnects

```
Check: Connection indicator in sidebar
Solution: Server auto-reconnects every 3s
```

### Frontend not loading

```
Check: http://localhost:8000
Solution: Ensure server is running and frontend/ directory exists
```

### No Traktor status updates

**Demo Mode:**
- Expected behavior, usa dati simulati

**Production Mode:**
- Verify Traktor is running
- Check MIDI connection: `python verify_midi_setup.py`
- Verify API keys in `autonomous_dj/config.py`

---

## 🚀 NEXT STEPS

### Immediate:

1. ✅ Test demo mode
2. ✅ Configure API keys
3. ✅ Test with Traktor

### Short-term:

- [ ] Add LLM integration for natural language parsing (OpenRouter)
- [ ] Implement autonomous mixing logic
- [ ] Add track selection AI
- [ ] Implement effects control

### Long-term:

- [ ] Voice control (Speech-to-Text)
- [ ] Mobile responsive design
- [ ] Mix history & analytics
- [ ] Playlist auto-generation
- [ ] Multi-user support

---

## 📚 DOCUMENTATION

**Related Files:**
- `CLAUDE.md` - Complete project overview
- `DJ_WORKFLOW_RULES.md` - DJ workflow rules
- `README_VISION_WORKFLOW.md` - Vision system guide
- `MIDI_INTERACTION_MODE_FIX.md` - MIDI setup

**API Documentation:**
- http://localhost:8000/docs (FastAPI auto-generated)

---

## 🎯 DEMO MODE vs PRODUCTION MODE

| Feature | Demo Mode | Production Mode |
|---------|-----------|-----------------|
| UI Interface | ✅ Full | ✅ Full |
| WebSocket | ✅ Simulated data | ✅ Real-time Traktor |
| Commands | ✅ Echo responses | ✅ Real MIDI control |
| Vision AI | ❌ | ✅ Claude Vision |
| Traktor Integration | ❌ | ✅ Full |
| API Keys Required | ❌ | ✅ Yes |

---

## 🤝 CONTRIBUTING

Contributions welcome! See `CLAUDE.md` for development guidelines.

---

## 📄 LICENSE

Private - All Rights Reserved

---

**For detailed technical documentation, see CLAUDE.md**

**Last Updated:** October 25, 2025
