# 🛠️ Setup Completo - Traktor AI

Guida dettagliata per configurare il sistema Traktor AI da zero.

---

## 📋 Indice

1. [Requisiti Sistema](#requisiti-sistema)
2. [Installazione Software](#installazione-software)
3. [Configurazione Traktor Pro 3](#configurazione-traktor-pro-3)
4. [Setup MIDI](#setup-midi)
5. [Installazione Python](#installazione-python)
6. [Configurazione API Keys](#configurazione-api-keys)
7. [Prima Esecuzione](#prima-esecuzione)
8. [Verifica Setup](#verifica-setup)

---

## 1. Requisiti Sistema

### Hardware Minimo

- **CPU**: Intel i5 / AMD Ryzen 5 (o superiore)
- **RAM**: 8 GB (16 GB raccomandati)
- **Storage**: 500 MB per il progetto + spazio per collection Traktor
- **Audio Interface**: ASIO-compatible (Windows) o CoreAudio (macOS)

### Sistema Operativo

#### Windows
- **OS**: Windows 10/11 (64-bit)
- **Audio Driver**: ASIO4ALL o audio interface dedicata
- **MIDI**: loopMIDI (virtual MIDI port)

#### macOS
- **OS**: macOS 10.15 Catalina o superiore
- **Audio Driver**: CoreAudio (built-in)
- **MIDI**: IAC Driver (built-in)

#### Linux
- **OS**: Ubuntu 20.04+ / Debian 11+
- **Audio Driver**: JACK Audio Connection Kit
- **MIDI**: ALSA MIDI (built-in)

---

## 2. Installazione Software

### Step 1: Traktor Pro 3

1. **Download**:
   - Vai a: https://www.native-instruments.com/en/products/traktor/dj-software/traktor-pro-3/
   - Scarica versione trial o completa

2. **Installazione**:
   ```bash
   # Windows: esegui installer .exe
   # macOS: apri .dmg e trascina in Applications
   # Linux: usa Wine (sperimentale)
   ```

3. **Prima esecuzione**:
   - Avvia Traktor Pro 3
   - Completa wizard iniziale
   - **CRITICO**: Salta per ora configurazione audio/MIDI

### Step 2: Virtual MIDI Port

#### Windows - loopMIDI

1. **Download**:
   - https://www.tobias-erichsen.de/software/loopmidi.html
   - Download: `loopMIDISetup_<version>.zip`

2. **Installazione**:
   ```bash
   # Estrai ZIP ed esegui installer
   # Default path: C:\Program Files (x86)\Tobias Erichsen\loopMIDI\
   ```

3. **Configurazione**:
   ```
   1. Apri loopMIDI
   2. Nel campo "New port-name": scrivi "Traktor MIDI Bus 1"
   3. Click "+" per creare porta
   4. Verifica: la porta appare nella lista
   ```

   **Screenshot atteso**:
   ```
   ┌─────────────────────────────────┐
   │ loopMIDI v1.0.16                │
   ├─────────────────────────────────┤
   │ Port name: Traktor MIDI Bus 1   │
   │ [+] [-] [Autostart]             │
   ├─────────────────────────────────┤
   │ Active ports:                   │
   │ • Traktor MIDI Bus 1            │
   └─────────────────────────────────┘
   ```

#### macOS - IAC Driver

1. **Apertura MIDI Setup**:
   ```bash
   # Spotlight Search (Cmd+Space)
   # Digita: "Audio MIDI Setup"
   # Oppure:
   open "/Applications/Utilities/Audio MIDI Setup.app"
   ```

2. **Configurazione**:
   ```
   1. Window → Show MIDI Studio (Cmd+2)
   2. Doppio click su "IAC Driver"
   3. Check "Device is online"
   4. Click "+" sotto "Ports"
   5. Rinomina porta: "IAC Driver Bus 1"
   6. Click "Apply"
   ```

#### Linux - ALSA MIDI

```bash
# Verifica ALSA MIDI modules
sudo modprobe snd-virmidi

# Crea 4 virtual MIDI ports
echo "snd-virmidi" | sudo tee -a /etc/modules

# Verifica ports disponibili
aconnect -l
```

### Step 3: Python

#### Windows

```bash
# Download da python.org
https://www.python.org/downloads/

# CRITICAL: Durante installazione
☑ Add Python to PATH
☑ Install pip

# Verifica installazione
python --version  # Deve essere 3.8+
pip --version
```

#### macOS

```bash
# Usa Homebrew (raccomandato)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install python@3.11

# Verifica
python3 --version
pip3 --version
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

### Step 4: Git

#### Windows

```bash
# Download Git for Windows
https://git-scm.com/download/win

# Durante installazione, scegli:
- Editor: Visual Studio Code (o default)
- PATH: "Git from the command line and also from 3rd-party software"
- Line ending: "Checkout Windows-style, commit Unix-style"
```

#### macOS

```bash
# Xcode Command Line Tools (include Git)
xcode-select --install

# Oppure via Homebrew
brew install git
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt install git

# Fedora
sudo dnf install git

# Arch
sudo pacman -S git
```

---

## 3. Configurazione Traktor Pro 3

### Step 1: Audio Setup

1. **Apri Preferences**:
   ```
   Traktor → Preferences (o Ctrl+P / Cmd+,)
   ```

2. **Audio Setup**:
   ```
   Left panel → Audio Setup

   Windows:
   • Audio Device: [Il tuo device ASIO]
   • ⚠️ CRITICAL: NON usare "WASAPI" - bloccherà MIDI!
   • Sample Rate: 44100 Hz o 48000 Hz
   • Latency: 512 samples (regola se necessario)

   macOS:
   • Audio Device: [Il tuo device CoreAudio]
   • Sample Rate: 44100 Hz
   • Latency: 512 samples

   Linux:
   • Audio Device: [JACK Audio]
   • Sample Rate: 48000 Hz
   ```

### Step 2: Controller Manager

1. **Apri Controller Manager**:
   ```
   Preferences → Controller Manager
   ```

2. **Importa TSI file**:
   ```
   1. Click "Import" (bottom-left)
   2. Seleziona: config/TraktorMIDIMapping.tsi
   3. Verifica: "Traktor MIDI Bus 1" appare nella lista
   ```

3. **CRITICAL - Interaction Mode**:
   ```
   ⚠️ QUESTO È IL SETTING PIÙ IMPORTANTE!

   Device → Generic MIDI → Device Target
   → "MIDI Interaction Mode" = "Direct"

   ❌ NON usare "Toggle" - causerà comportamento imprevedibile!
   ```

### Step 3: Collection Setup

1. **Importa music library**:
   ```
   File → Import Music Folder
   → Seleziona cartella con la tua musica
   ```

2. **Analizza tracce** (CRITICAL per Camelot Wheel):
   ```
   1. Browser → seleziona tutte le tracce (Ctrl+A / Cmd+A)
   2. Right-click → Analyze (async) → All
   3. ⚠️ Attendi completamento analisi BPM
   4. Right-click → Analyze (async) → Determine Key
   5. ⚠️ Attendi completamento analisi key
   ```

   **Tempo stimato**: ~1-2 minuti per 100 tracce

3. **Verifica analisi**:
   ```
   Nel browser, le colonne devono mostrare:
   • BPM: valori numerici (es. 128.00)
   • KEY: valori come "8A", "5B", etc.
   ```

---

## 4. Setup MIDI

### Verifica MIDI Port

#### Windows

```bash
# Apri PowerShell
Get-PnpDevice | Where-Object {$_.FriendlyName -like "*MIDI*"}

# Output atteso:
# Status     Class           FriendlyName
# ------     -----           ------------
# OK         MEDIA           loopMIDI Port
# OK         MEDIA           Traktor MIDI Bus 1
```

#### macOS

```bash
# Lista MIDI devices
ls /dev/cu.*

# Output atteso:
# /dev/cu.IAC-Driver-Bus-1
```

### Test MIDI Loopback

```bash
# Clone repo (se non già fatto)
git clone https://github.com/Fiore0312/traktor.git
cd traktor

# Attiva venv
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Installa dipendenze
pip install -r requirements.txt

# Test MIDI
python verify_midi_setup.py
```

**Output atteso**:
```
🎛️ Traktor MIDI Setup Verification
====================================

✅ MIDI Backend: mido (with pygame backend)
✅ Available MIDI Ports:
   • Traktor MIDI Bus 1

✅ MIDI Driver initialized successfully
✅ Port: Traktor MIDI Bus 1

🎉 MIDI Setup Complete!
```

**Se vedi errori**, vai a [TROUBLESHOOTING.md](TROUBLESHOOTING.md#midi-non-funziona)

---

## 5. Installazione Python

### Clone Repository

```bash
# Via HTTPS
git clone https://github.com/Fiore0312/traktor.git
cd traktor

# Via SSH (se hai configurato SSH key)
git clone git@github.com:Fiore0312/traktor.git
cd traktor
```

### Virtual Environment Setup

```bash
# Crea virtual environment
python -m venv venv

# Attiva venv
# Windows (Command Prompt)
.\venv\Scripts\activate.bat

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

# Verifica attivazione (dovresti vedere "(venv)" nel prompt)
```

### Installazione Dipendenze

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Installa requirements
pip install -r requirements.txt

# Windows: se errore "externally-managed-environment"
pip install -r requirements.txt --break-system-packages

# Verifica installazione
pip list | grep -E "mido|rtmidi|flask|anthropic|requests"
```

**Output atteso**:
```
anthropic              0.x.x
Flask                  3.x.x
mido                   1.3.x
pygame                 2.6.x  (Windows)
python-rtmidi          1.5.x  (macOS)
requests               2.31.x
```

---

## 6. Configurazione API Keys

### Creazione Config File

```bash
# Copia template
cp autonomous_dj/config.template.py autonomous_dj/config.py

# Windows Command Prompt
copy autonomous_dj\config.template.py autonomous_dj\config.py
```

### Ottenere API Keys

#### Anthropic Claude (Opzionale - per Vision mode)

1. **Registrazione**:
   - Vai a: https://console.anthropic.com/
   - Click "Sign Up" → completa registrazione
   - Verifica email

2. **Crea API Key**:
   ```
   Console → Settings → API Keys
   → "Create Key"
   → Nome: "Traktor AI - Vision"
   → Click "Create"
   → ⚠️ COPIA SUBITO la key (visibile una sola volta!)
   ```

3. **Costi**:
   - **Free tier**: $5 crediti iniziali
   - **Vision API**: ~$0.003 per richiesta
   - **Durata stimata**: ~1600 richieste con $5

#### OpenRouter (Gratuito - per LLM)

1. **Registrazione**:
   - Vai a: https://openrouter.ai/
   - Click "Sign Up" → login con Google/GitHub

2. **Crea API Key**:
   ```
   Dashboard → Keys
   → "Create New Key"
   → Nome: "Traktor AI"
   → Click "Create"
   → COPIA la key
   ```

3. **Modelli Gratuiti**:
   - `meta-llama/llama-3.2-3b-instruct:free`
   - `deepseek/deepseek-chat`
   - `google/gemini-2.0-flash-exp:free`

### Editare Config File

```bash
# Apri con editor preferito
# Windows
notepad autonomous_dj\config.py

# macOS
nano autonomous_dj/config.py

# Linux
vim autonomous_dj/config.py
```

**Contenuto `config.py`**:

```python
"""
Traktor AI Configuration
⚠️ NEVER commit this file to Git!
"""

# =============================================================================
# API KEYS
# =============================================================================

# Anthropic Claude API (opzionale - per Vision mode)
# Get from: https://console.anthropic.com/settings/keys
# Cost: ~$0.003 per request
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR-ACTUAL-KEY-HERE"

# OpenRouter API (gratuito - per LLM)
# Get from: https://openrouter.ai/keys
# Free models available!
OPENROUTER_API_KEY = "sk-or-v1-YOUR-ACTUAL-KEY-HERE"

# =============================================================================
# SYSTEM CONFIG
# =============================================================================

# Vision mode (True = usa Claude Vision, False = blind mode gratuito)
USE_VISION = False  # Default: False per evitare costi

# MIDI port name
MIDI_PORT_NAME = "Traktor MIDI Bus 1"  # Windows
# MIDI_PORT_NAME = "IAC Driver Bus 1"  # macOS

# Server settings
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8000

# Debug mode
DEBUG = True
```

### Verifica Config

```bash
# Test import config
python -c "from autonomous_dj.config import OPENROUTER_API_KEY; print('✅ Config loaded successfully')"

# Se errore: verifica syntax in config.py
```

---

## 7. Prima Esecuzione

### Parse Traktor Collection

```bash
# Parse collection.nml → crea tracks.db
python collection_parser_xml.py

# Output atteso:
# 🎵 Parsing Traktor Collection...
# ✅ Found collection: C:\Users\...\collection.nml
# ✅ Parsing 393 tracks...
# ✅ Database created: tracks.db (393 tracks)
```

### Avvia Server

```bash
# Windows
START_SERVER_PRODUCTION.bat

# macOS/Linux
python autonomous_dj/workflow_controller.py
```

**Output atteso**:
```
🎛️ Traktor AI - Autonomous DJ System
=====================================

✅ MIDI Driver initialized
✅ Port: Traktor MIDI Bus 1
✅ Vision mode: BLIND (free)
✅ OpenRouter client ready
✅ Camelot matcher loaded (393 tracks)

🌐 Server started: http://localhost:8000

Press Ctrl+C to stop
```

### Primo Test

1. **Apri browser**: http://localhost:8000

2. **Test web interface**:
   - Click "🎧 Auto-Select Compatible"
   - Dovresti vedere log nel server

3. **Test comando naturale**:
   ```
   Scrivi nella chat: "Trova una traccia compatibile"
   ```

4. **Verifica Traktor**:
   - Osserva browser Traktor
   - Dovrebbe navigare automaticamente
   - Traccia compatibile caricata su deck

---

## 8. Verifica Setup

### Checklist Completa

```bash
# 1. MIDI Connection
python verify_midi_setup.py
# ✅ Expected: "MIDI Setup Complete!"

# 2. Collection Database
ls -lh tracks.db
# ✅ Expected: file exists, size > 100 KB

# 3. Config File
python -c "from autonomous_dj.config import OPENROUTER_API_KEY; print('OK')"
# ✅ Expected: "OK"

# 4. Traktor Running
# ✅ Manualmente: verifica Traktor Pro 3 aperto

# 5. Audio Device
# ✅ Traktor Preferences → Audio Setup → deve essere ASIO (Windows)

# 6. MIDI Interaction Mode
# ✅ Traktor Preferences → Controller Manager → "Direct" mode
```

### Test Completo Integration

```bash
# Run integration test suite
python test_intelligent_integration.py

# Expected output:
# ✅ Test 1: MIDI Driver
# ✅ Test 2: Collection Parser
# ✅ Test 3: Camelot Matcher
# ✅ Test 4: Track Navigation
# ✅ Test 5: End-to-End Workflow
#
# 🎉 All tests passed!
```

### Troubleshooting

Se qualcosa non funziona:

1. **MIDI errors** → [TROUBLESHOOTING.md#midi-non-funziona](TROUBLESHOOTING.md#midi-non-funziona)
2. **Vision errors** → [TROUBLESHOOTING.md#vision-api-errors](TROUBLESHOOTING.md#vision-api-errors)
3. **Collection errors** → [TROUBLESHOOTING.md#collection-non-trovata](TROUBLESHOOTING.md#collection-non-trovata)

---

## 🎉 Setup Completato!

Ora sei pronto per usare Traktor AI!

**Next steps**:

1. **Leggi**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - capire come funziona tutto insieme
2. **Esplora**: [API_REFERENCE.md](API_REFERENCE.md) - API disponibili
3. **Impara**: [CAMELOT_WHEEL_GUIDE.md](CAMELOT_WHEEL_GUIDE.md) - teoria harmonic mixing

**Comandi utili**:

```bash
# Avvia server
START_SERVER_PRODUCTION.bat

# Stop server
Ctrl+C

# Re-parse collection (dopo aver aggiunto tracce)
python collection_parser_xml.py

# Update dipendenze
pip install -r requirements.txt --upgrade

# Backup collection
cp traktor_collection.nml data/backups/collection_$(date +%Y%m%d).nml
```

---

**Per supporto**: [GitHub Issues](https://github.com/Fiore0312/traktor/issues)

*Last updated: October 26, 2025*
