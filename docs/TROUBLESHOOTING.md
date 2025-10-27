# 🔧 Troubleshooting - Traktor AI

Guida completa alla risoluzione dei problemi più comuni del sistema Traktor AI.

---

## 📋 Indice Problemi

1. [MIDI Non Funziona](#1-midi-non-funziona)
2. [Vision API Errors](#2-vision-api-errors)
3. [Collection Non Trovata](#3-collection-non-trovata)
4. [Server Non Si Avvia](#4-server-non-si-avvia)
5. [Track Selection Fails](#5-track-selection-fails)
6. [Performance Issues](#6-performance-issues)
7. [Traktor Non Risponde](#7-traktor-non-risponde)
8. [Database Corruption](#8-database-corruption)

---

## 1. MIDI Non Funziona

### Sintomo

```
❌ MIDIDriverError: No MIDI ports available
❌ Could not open MIDI port "Traktor MIDI Bus 1"
```

### Diagnosi

```bash
# Check MIDI ports
python verify_midi_setup.py

# Windows: check loopMIDI
tasklist | findstr loopMIDI

# macOS: check IAC Driver
ls /dev/cu.*
```

### Soluzione 1: Verifica loopMIDI (Windows)

```bash
# 1. Apri loopMIDI
C:\Program Files (x86)\Tobias Erichsen\loopMIDI\loopMIDI.exe

# 2. Verifica porta "Traktor MIDI Bus 1" esistente
# 3. Se mancante: crea nuova porta
#    Nome: "Traktor MIDI Bus 1"
#    Click "+" per aggiungere

# 4. Riavvia Traktor
# 5. Riavvia server Traktor AI
```

### Soluzione 2: Audio Driver Check (CRITICAL!)

```
⚠️ TRAKTOR DEVE USARE ASIO, NON WASAPI!

WASAPI blocca MIDI su Windows!

Fix:
1. Traktor → Preferences → Audio Setup
2. Audio Device: Seleziona un device ASIO
   - Se hai audio interface: usa quello
   - Altrimenti: installa ASIO4ALL (https://asio4all.org/)
3. Riavvia Traktor
4. Test MIDI: python verify_midi_setup.py
```

### Soluzione 3: MIDI Interaction Mode

```
⚠️ CRITICAL SETTING!

1. Traktor → Preferences → Controller Manager
2. Device → Generic MIDI
3. Device Target → "MIDI Interaction Mode"
4. DEVE essere "Direct" (NON "Toggle"!)
5. Apply → OK
6. Riavvia Traktor
```

### Soluzione 4: Port Name Mismatch

```python
# Edit config
nano autonomous_dj/config.py

# Windows
MIDI_PORT_NAME = "Traktor MIDI Bus 1"

# macOS
MIDI_PORT_NAME = "IAC Driver Bus 1"

# Linux
MIDI_PORT_NAME = "Virtual MIDI 1"

# Verifica nome esatto
python -c "import mido; print(mido.get_output_names())"
```

---

## 2. Vision API Errors

### Sintomo

```
❌ AnthropicAPIError: invalid_api_key
❌ Rate limit exceeded
❌ Insufficient credits
```

### Soluzione 1: API Key Invalid

```bash
# Check API key
python -c "from autonomous_dj.config import ANTHROPIC_API_KEY; print(ANTHROPIC_API_KEY[:15])"

# Should show: sk-ant-api03-...

# If error:
# 1. Verify config.py exists
cp autonomous_dj/config.template.py autonomous_dj/config.py

# 2. Edit and paste correct key
nano autonomous_dj/config.py

# 3. Get new key if needed
# https://console.anthropic.com/settings/keys
```

### Soluzione 2: Rate Limit

```python
# Edit workflow_controller.py
# Add rate limiting

from time import sleep

def analyze_with_vision_rate_limited(screenshot):
    sleep(1.5)  # Max 40 requests/min (Anthropic tier 1)
    return claude_vision_client.analyze(screenshot)
```

### Soluzione 3: Credits Exhausted

```bash
# Check credits
# https://console.anthropic.com/settings/billing

# Options:
# 1. Add payment method
# 2. Switch to Blind mode (FREE!)

# Edit config
nano autonomous_dj/config.py
USE_VISION = False  # Disable Vision

# Restart server
```

### Soluzione 4: Fallback to Blind Mode

```python
# Auto-fallback in code
try:
    state = vision_system.get_state()
except VisionAPIError as e:
    logger.warning(f"Vision failed: {e}, using blind mode")
    state = {"bpm": 128, "key": "8A"}
```

---

## 3. Collection Non Trovata

### Sintomo

```
❌ FileNotFoundError: collection.nml not found
❌ Database empty (0 tracks)
```

### Soluzione 1: Parse Collection

```bash
# Find collection.nml
# Windows
dir /s collection.nml

# macOS/Linux
find ~ -name "collection.nml"

# Common paths:
# Windows: C:\Users\<user>\Documents\Native Instruments\Traktor\collection.nml
# macOS: ~/Documents/Native Instruments/Traktor/collection.nml

# Parse collection
python collection_parser_xml.py

# Verifica database creato
ls -lh tracks.db  # Should be > 100 KB
```

### Soluzione 2: Database Permissions

```bash
# Check write permissions
# Windows
icacls tracks.db

# macOS/Linux
ls -la tracks.db
chmod 644 tracks.db  # If needed
```

### Soluzione 3: Re-Create Database

```bash
# Backup old database
mv tracks.db tracks.db.backup

# Re-parse collection
python collection_parser_xml.py

# Verify tracks count
sqlite3 tracks.db "SELECT COUNT(*) FROM tracks;"
```

---

## 4. Server Non Si Avvia

### Sintomo

```
❌ OSError: [Errno 48] Address already in use
❌ ModuleNotFoundError: No module named 'flask'
```

### Soluzione 1: Port Already In Use

```bash
# Check what's using port 8000
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# Kill process
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>

# Or use different port
# Edit config
SERVER_PORT = 8001  # In config.py
```

### Soluzione 2: Missing Dependencies

```bash
# Reinstall requirements
pip install -r requirements.txt

# If error "externally-managed-environment"
pip install -r requirements.txt --break-system-packages

# Or use venv
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Soluzione 3: Python Version

```bash
# Check Python version
python --version

# Need 3.8+
# If older: update Python
# Windows: https://www.python.org/downloads/
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

---

## 5. Track Selection Fails

### Sintomo

```
❌ No compatible tracks found
❌ Navigation timeout
❌ Track loaded on wrong deck
```

### Soluzione 1: No Compatible Tracks

```bash
# Check database content
sqlite3 tracks.db

# Query
SELECT key, COUNT(*) FROM tracks GROUP BY key;

# If only 1-2 keys: need more tracks analyzed

# Fix: Analyze keys in Traktor
# 1. Traktor → Browser
# 2. Select All (Ctrl+A)
# 3. Right-click → Analyze → Determine Key
# 4. Wait for analysis complete
# 5. Re-parse: python collection_parser_xml.py
```

### Soluzione 2: BPM Range Too Narrow

```python
# Edit camelot_matcher.py
# Increase BPM tolerance

BPM_TOLERANCE = 0.10  # 10% instead of 6%

# Or pass param
compatible = matcher.find_compatible(
    current_key="8A",
    current_bpm=128.0,
    bpm_tolerance=0.12  # 12%
)
```

### Soluzione 3: Navigation Timeout

```python
# Edit midi_navigator.py
# Increase delays

DELAYS = {
    "folder_navigation": 0.5,  # Increase from 0.3
    "track_navigation": 0.3    # Increase from 0.2
}
```

---

## 6. Performance Issues

### Sintomo

```
⚠️ Slow response (>5 seconds)
⚠️ High CPU usage
⚠️ Memory leaks
```

### Soluzione 1: Disable Vision

```python
# Vision API adds ~800ms latency
# If not needed: disable

USE_VISION = False  # In config.py
```

### Soluzione 2: Database Indexing

```sql
-- Add indexes for faster queries
sqlite3 tracks.db

CREATE INDEX idx_key ON tracks(key);
CREATE INDEX idx_bpm ON tracks(bpm);
CREATE INDEX idx_key_bpm ON tracks(key, bpm);
```

### Soluzione 3: Caching

```python
# Add caching to avoid repeated queries
from functools import lru_cache

@lru_cache(maxsize=100)
def find_compatible_tracks_cached(key, bpm):
    return find_compatible_tracks(key, bpm)
```

---

## 7. Traktor Non Risponde

### Sintomo

```
⚠️ MIDI commands sent but Traktor doesn't react
⚠️ Browser doesn't navigate
```

### Soluzione 1: Traktor Focus

```
Traktor window deve avere focus!

Fix:
1. Click su Traktor window
2. Invia comando MIDI
3. Traktor dovrebbe reagire

Auto-focus (Windows):
# PowerShell
Add-Type @"
  using System;
  using System.Runtime.InteropServices;
  public class WinAPI {
    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
  }
"@
$traktor = Get-Process -Name "Traktor" -ErrorAction SilentlyContinue
[WinAPI]::SetForegroundWindow($traktor.MainWindowHandle)
```

### Soluzione 2: TSI Mapping Check

```
1. Traktor → Preferences → Controller Manager
2. Verify "Generic MIDI" device present
3. Check mappings:
   - CC 16 → Browser Folder Up/Down
   - CC 17 → Browser Track Up/Down
   - CC 18 → Load Deck A
   - CC 19 → Load Deck B

4. If missing:
   - Import TSI: config/TraktorMIDIMapping.tsi
```

### Soluzione 3: MIDI Learn

```
If specific CC not working:

1. Traktor → Preferences → Controller Manager
2. Add → Generic MIDI
3. Add In/Out:
   - Type: "Browser"
   - Assignment: "Navigate Folder Down"
4. Learn MIDI:
   - Click "Learn"
   - Send CC from Python: midi_driver.send_cc(16, 127)
   - Should auto-assign
```

---

## 8. Database Corruption

### Sintomo

```
❌ sqlite3.DatabaseError: database disk image is malformed
❌ Tracks count mismatch
```

### Soluzione 1: Integrity Check

```sql
sqlite3 tracks.db

-- Check integrity
PRAGMA integrity_check;

-- If errors: export and rebuild
.output tracks_backup.sql
.dump
.quit

# Rebuild
rm tracks.db
sqlite3 tracks.db < tracks_backup.sql
```

### Soluzione 2: Re-Parse Collection

```bash
# Delete corrupted database
rm tracks.db

# Re-parse from collection.nml
python collection_parser_xml.py

# Verify
sqlite3 tracks.db "SELECT COUNT(*) FROM tracks;"
```

---

## 🆘 Emergency Reset

Se NIENTE funziona:

```bash
# 1. Backup config
cp autonomous_dj/config.py autonomous_dj/config.backup.py

# 2. Clean install
rm -rf venv/
rm tracks.db
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Restore config
cp autonomous_dj/config.backup.py autonomous_dj/config.py

# 4. Re-parse collection
python collection_parser_xml.py

# 5. Test
python verify_midi_setup.py
python test_intelligent_integration.py

# 6. Start server
START_SERVER_PRODUCTION.bat
```

---

## 📞 Get Help

Se il problema persiste:

1. **GitHub Issues**: https://github.com/Fiore0312/traktor/issues
2. **Logs**: Controlla `data/logs/traktor_ai.log`
3. **Debug Mode**: Set `DEBUG=True` in config.py

**Quando apri issue, includi**:
- OS e versione
- Python version
- Output di `python verify_midi_setup.py`
- Relevant logs from `data/logs/`

---

*Last updated: October 26, 2025*
