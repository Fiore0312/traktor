# Integrated Vision Navigation + Track Loading Workflow

## Overview

Il sistema ora supporta comandi naturali che combinano navigazione e caricamento tracce in un unico workflow intelligente.

## Esempio di Comando

```
Utente: "cerca nella cartella Dub una traccia qualsiasi e cominciamo il set"
```

## Workflow Automatico

### 1. Parsing Intelligente (OpenRouter LLM)
```json
{
    "action": "LOAD_TRACK",
    "deck": "A",
    "folder": "dub",
    "confidence": 0.9
}
```

L'LLM riconosce che:
- Azione primaria: caricare una traccia
- Contesto: cartella "Dub"
- Deck: A (default per primo caricamento)

### 2. Navigazione Automatica (se folder specificata)
```python
if plan.get('folder'):
    # Vision-guided navigation
    nav_result = self._action_navigate_folder({'folder': folder})

    # Workflow:
    # 1. Capture screenshot
    # 2. Claude Vision legge folder names
    # 3. Calcola steps per raggiungere "Dub"
    # 4. MIDI commands: navigate_up/down, expand_collapse
    # 5. Verifica arrivo
```

### 3. Selezione Traccia Automatica
```python
# Dopo navigazione, seleziona prima traccia
self.midi.browser_scroll_tracks(direction=1)
time.sleep(0.5)
```

**CC MIDI inviato:**
- `BROWSER_SCROLL_LIST` (CC 74): scroll down → seleziona prima traccia

### 4. Caricamento Traccia
```python
# Safety check
if self.safety.pre_load_safety_check(deck):
    # Load track
    self.midi.load_track_deck_a()  # CC 27

    # Post-load safety
    self.safety.post_load_safety_setup(deck)
    # - Volume a 0
    # - Crossfader posizionato
```

### 5. Risposta all'Utente
```
"Track 'Some Dub Track.mp3' caricata su Deck A!
Volume impostato a 0 per sicurezza."
```

## Comandi Supportati

### Navigazione + Caricamento (Integrato)
```
"cerca nella cartella Dub una traccia qualsiasi e cominciamo il set"
"carica un brano Techno su Deck A"
"trova qualcosa nella cartella House"
"load a track from the Trance folder"
```

### Solo Navigazione
```
"naviga fino alla cartella Dub"
"Navigate to the Techno folder"
"trova la cartella House"
```

### Solo Caricamento (traccia già selezionata)
```
"carica questa traccia su Deck A"
"load this track on Deck B"
```

## Flusso Completo dei Comandi MIDI

### Navigazione alla Cartella
```
1. BROWSER_SCROLL_TREE_DEC (CC 73, value=1)  → Navigate up
2. BROWSER_SCROLL_TREE_INC (CC 72, value=1)  → Navigate down
3. BROWSER_EXPAND_COLLAPSE (CC 64, value=127) → Expand/collapse node
```

### Selezione Traccia
```
4. BROWSER_SCROLL_LIST (CC 74, value=1)      → Scroll down (select track)
```

### Caricamento
```
5. DECK_A_LOAD_TRACK (CC 27, value=127)      → Load to Deck A
   o
   DECK_B_LOAD_TRACK (CC 28, value=127)      → Load to Deck B
```

### Safety Setup
```
6. DECK_A_VOLUME (CC 4, value=0)             → Volume a 0
   o
   DECK_B_VOLUME (CC 5, value=0)
7. CROSSFADER_POSITION (CC 8, value=0/127)   → Crossfader left/right
```

## Timing e Delays

```python
# Navigazione
time.sleep(0.3)  # Tra ogni comando navigate_up/down
time.sleep(0.5)  # Dopo expand_collapse

# Selezione traccia
time.sleep(0.5)  # Dopo browser_scroll_tracks

# Caricamento
time.sleep(2.0)  # Dopo load_track (Traktor loading time)
```

## Gestione Errori

### Cartella Non Trovata
```
Risposta: "Non riesco a navigare alla cartella 'xyz'.
           Prova a posizionarti manualmente più vicino."
```

**Possibili cause:**
- Cartella non esiste
- Cartella troppo annidata
- Vision non riesce a leggere i nomi

**Soluzione:**
- Naviga manualmente più vicino alla cartella target
- Verifica che la cartella esista in Traktor

### Nessuna Traccia Selezionata
```
Risposta: "Nessuna traccia evidenziata nel browser.
           Seleziona una traccia prima."
```

**Possibili cause:**
- Cartella vuota
- browser_scroll_tracks non ha funzionato

**Soluzione:**
- Il sistema ora fa 2 tentativi di scroll automatico
- Se fallisce, seleziona manualmente una traccia

### Safety Check Fallito
```
Risposta: "Safety check failed per Deck A"
```

**Possibili cause:**
- Deck già in play
- Volume troppo alto
- Altre condizioni unsafe

**Soluzione:**
- Sistema applica automaticamente safety measures
- Raramente dovrebbe verificarsi

## Codice Chiave

### workflow_controller.py: _action_load_track()

```python
def _action_load_track(self, plan: Dict) -> Dict:
    deck = plan['deck']
    folder = plan.get('folder')

    # STEP 0: Navigate to folder if specified
    if folder:
        print(f"[CONTROLLER] Navigating to folder '{folder}'...")
        nav_result = self._action_navigate_folder({'folder': folder})

        if not nav_result['success']:
            return {'success': False, 'message': f"Non riesco a navigare..."}

        # Select first track
        self.midi.browser_scroll_tracks(direction=1)
        time.sleep(0.5)

    # STEP 1: Capture and analyze
    screenshot = self.vision.capture_traktor_window()
    analysis = self.ai_vision.analyze_traktor_screenshot(screenshot)

    # STEP 2: Check track highlighted
    if not analysis['browser']['track_highlighted']:
        # Try scrolling to select
        self.midi.browser_scroll_tracks(direction=1)
        time.sleep(0.5)

        # Re-check
        screenshot = self.vision.capture_traktor_window()
        analysis = self.ai_vision.analyze_traktor_screenshot(screenshot)

        if not analysis['browser']['track_highlighted']:
            return {'success': False, 'message': "Nessuna traccia..."}

    # STEP 3: Safety check
    if not self.safety.pre_load_safety_check(deck):
        return {'success': False, 'message': "Safety check failed"}

    # STEP 4: Load track
    if deck == 'A':
        self.midi.load_track_deck_a()
    else:
        self.midi.load_track_deck_b()

    time.sleep(2)

    # STEP 5: Post-load safety
    self.safety.post_load_safety_setup(deck)

    track_name = analysis['browser']['track_highlighted']
    return {
        'success': True,
        'message': f"Track '{track_name}' caricata su Deck {deck}!"
    }
```

## Test

### Test Completo via Frontend
```bash
# 1. Avvia server
RUN_PRODUCTION_SERVER.bat

# 2. Apri browser
http://localhost:8000

# 3. Verifica Traktor aperto con browser visibile

# 4. Digita nella chat:
"cerca nella cartella Dub una traccia qualsiasi e cominciamo il set"

# 5. Osserva:
[CONTROLLER] User command: cerca nella cartella Dub...
[CONTROLLER] Navigating to folder 'dub' before loading track...
[BROWSER NAV] Starting navigation to 'dub'
[BROWSER NAV] Attempt 1/15
[BROWSER NAV] Current folder: Collection
[BROWSER NAV] Target visible, navigating to it...
[BROWSER NAV] Need 3 steps
[BROWSER NAV] ✓ Successfully navigated to 'dub'
[CONTROLLER] Selecting first track in folder...
[CONTROLLER] Track 'Some Dub Track.mp3' caricata su Deck A!
```

### Test Navigazione Standalone
```bash
TEST_BROWSER_NAVIGATION.bat
```

## Vantaggi del Workflow Integrato

1. **Un Comando = Workflow Completo**
   - Non serve dire "naviga a dub" E POI "carica traccia"
   - Tutto automatico in un unico comando

2. **Intelligente**
   - LLM capisce intent anche con linguaggio naturale vario
   - Vision-guided navigation trova la cartella da solo

3. **Sicuro**
   - Safety checks integrati
   - Volume sempre a 0 dopo load
   - Verifiche pre e post caricamento

4. **Robusto**
   - Fallback automatici
   - Re-tentativi per selezione traccia
   - Gestione errori completa

## Prossimi Passi

Con questo workflow ora puoi:

1. **Caricare prima traccia**: "cerca nella cartella Dub una traccia e iniziamo"
2. **Caricare seconda traccia**: "trova un brano Techno per Deck B"
3. **Iniziare mix**: "play Deck A"
4. **Transizione**: "sync Deck B e alza il volume"

Il sistema gestisce tutto automaticamente, dalla navigazione al caricamento, alla safety!

---

**Status:** Production Ready ✓
**Last Updated:** 2025-10-25
