# Quick Start - Production Mode (con Traktor)

## Prerequisiti

### 1. Traktor Pro 3
- ✅ Deve essere **aperto e funzionante**
- ✅ Una traccia caricata sul browser (per testare)

### 2. loopMIDI
- ✅ Configurato con "Traktor MIDI Bus 1"
- ✅ Porta MIDI virtuale attiva

### 3. ASIO Driver
- ✅ **IMPORTANTE**: Audio Device = ASIO (NOT WASAPI!)
- ✅ WASAPI blocca il MIDI
- ✅ Se non hai ASIO nativo, installa ASIO4ALL

### 4. MIDI Interaction Mode
- ✅ **CRITICO**: Preferences → Controller Manager
- ✅ Generic MIDI device
- ✅ Interaction Mode = "Direct" (NOT Toggle/Hold)

### 5. API Keys
- ✅ Già configurate in `autonomous_dj/config.py`

## Avvio Server Production

### Metodo 1: Batch File (Consigliato)
```
Double-click su: START_SERVER_PRODUCTION.bat
```

### Metodo 2: Command Line
```bash
cd C:\traktor
.\venv\Scripts\python.exe -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### Metodo 3: Activate venv first
```bash
cd C:\traktor
.\venv\Scripts\activate
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

## Apertura Frontend

Apri browser: **http://localhost:8000**

## Test Funzionalità

### 1. Verifica Connessione
- Guarda il pallino verde nella sidebar (WebSocket connesso)
- Status dovrebbe mostrare stato reale di Traktor

### 2. Test Comandi Base

**Mostra Status:**
```
Mostrami lo stato
```

**Carica Traccia:**
```
Carica una traccia su Deck A
```

**Play:**
```
Fai play su Deck A
```

**Stop:**
```
Ferma Deck A
```

### 3. Test Vision System

Il sistema dovrebbe:
- ✅ Catturare screenshot di Traktor (tutti gli schermi)
- ✅ Analizzare UI con Claude Vision API
- ✅ Estrarre info: tracce, BPM, stato deck
- ✅ Aggiornare status ogni 2 secondi via WebSocket

## Differenze Demo vs Production

| Feature | Demo Mode | Production Mode |
|---------|-----------|-----------------|
| UI | ✅ Completa | ✅ Completa |
| WebSocket | ✅ Simulato | ✅ Reale |
| Comandi | ❌ Echo | ✅ MIDI Control |
| Vision AI | ❌ | ✅ Claude Vision |
| Traktor | ❌ | ✅ Controllo reale |
| API Keys | ❌ | ✅ Richieste |

## Troubleshooting

### Server non si avvia

**Errore Import:**
```
ModuleNotFoundError: No module named 'autonomous_dj.generated.traktor_vision'
```

**Soluzione:**
```bash
cd C:\traktor
.\venv\Scripts\python.exe verify_midi_setup.py
```

### WebSocket non si connette

- Verifica che il server sia running
- Controlla F12 → Console per errori JavaScript
- Il client riprova ogni 3 secondi automaticamente

### Comandi non funzionano

**Verifica MIDI:**
```bash
cd C:\traktor
.\venv\Scripts\python.exe verify_midi_setup.py
```

**Verifica loopMIDI:**
- Apri loopMIDI
- Controlla che "Traktor MIDI Bus 1" sia attivo

**Verifica Traktor:**
- Preferences → Audio Setup → Audio Device = ASIO
- Preferences → Controller Manager → Interaction Mode = Direct

### Vision System non funziona

**Test Vision:**
```bash
cd C:\traktor
.\venv\Scripts\python.exe test_vision_simple.py
```

Questo dovrebbe:
1. Catturare screenshot
2. Chiamare Claude Vision API
3. Mostrare analisi UI

## Log e Debug

I log del server appariranno nella console dove hai lanciato il server.

Per salvare log:
```bash
cd C:\traktor
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload > logs/server.log 2>&1
```

## Comandi Utili

### Verifica Status via API
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/status
```

### Invia Comando via API
```bash
curl -X POST http://localhost:8000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "Mostrami lo stato"}'
```

## Prossimi Passi

1. ✅ Avvia server production
2. ✅ Testa comandi base
3. ✅ Verifica vision system
4. ✅ Testa mix completo

## Documentazione Completa

- `CLAUDE.md` - Panoramica progetto
- `README_FULLSTACK_APP.md` - Guida applicazione
- `DJ_WORKFLOW_RULES.md` - Regole DJ
- `README_VISION_WORKFLOW.md` - Sistema vision
- http://localhost:8000/docs - API docs (quando server running)
