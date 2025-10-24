# 🤖 Usare Claude Code con Questo Progetto

## Differenza: claude vs code

### `claude` - Claude Code (AI Assistant)
- **Cosa fa**: Apre Claude Code nel terminale
- **Quando usare**: Per lavorare con AI assistant
- **Comando**: `claude`

### `code .` - VS Code (Editor)  
- **Cosa fa**: Apre VS Code normale
- **Quando usare**: Per editing manuale
- **Comando**: `code .`

## 🚀 Come Usare Claude Code

### 1. Preparazione (una volta)

```bash
cd /c/traktor
source activate.sh
pip install -r requirements.txt
```

### 2. Avvia Claude Code

```bash
claude
```

Claude Code si aprirà nel terminale e caricherà automaticamente:
- ✅ `claude.md` - Contesto del progetto
- ✅ `.claude/skills/traktor-dj-autonomous/SKILL.md` - Skill completa
- ✅ Tutto il codice della cartella

### 3. Esempi di Richieste

```
"Carica una traccia Techno sul deck A"

"Verifica lo stato della connessione MIDI"

"Spiega come funziona il workflow MASTER/SYNC"

"Mostra i moduli disponibili in autonomous_dj/generated"

"Crea uno script per testare il browser navigator"

"Analizza il file deck_operations.py"

"Help me fix the MIDI connection issue"

"Create a new function to load tracks by BPM range"
```

### 4. Claude Code Capisce Automaticamente

- 🎯 **Skill System**: Legge `.claude/skills/traktor-dj-autonomous/SKILL.md`
- 📋 **Workflow Rules**: Conosce `DJ_WORKFLOW_RULES.md`
- 🔧 **Configurazioni**: Usa `config/traktor_midi_mapping.json`
- 💾 **Moduli**: Sa quali moduli esistono e come usarli

## 💡 Cosa Claude Code Può Fare

### Modificare Codice
```
"Aggiungi una funzione per controllare il volume del deck B"
"Ottimizza il timing del browser navigator"
"Fix the bug in mix_executor.py"
```

### Creare Nuovi File
```
"Crea uno script per testare tutte le funzioni MIDI"
"Create a new module for playlist management"
"Make a debug utility for MIDI commands"
```

### Analizzare e Spiegare
```
"Spiega come funziona persistent_memory.py"
"Analizza il workflow di caricamento traccia"
"What does the energy_analyzer module do?"
```

### Troubleshooting
```
"Il MIDI non funziona, cosa controllo?"
"Debug the browser navigation timing issue"
"Why is the MASTER/SYNC logic not working?"
```

## 🔄 Workflow Tipico

```bash
# 1. Attiva venv
cd /c/traktor
source activate.sh

# 2. Avvia Claude Code
claude

# 3. Chatta con Claude
> "Show me the structure of deck_operations.py"
> "Create a test script for loading tracks"
> "Help me understand the MIDI timing requirements"

# 4. Claude modifica i file quando necessario
# I file vengono salvati automaticamente

# 5. Testa il codice
python verify_midi_setup.py
python <nuovo_script_creato>.py

# 6. Continua il ciclo
```

## ⚙️ Configurazione Automatica

Claude Code legge automaticamente:

### 1. claude.md (root)
Contesto generale del progetto:
- Architettura
- Setup
- Quick start
- Regole principali

### 2. .claude/skills/traktor-dj-autonomous/SKILL.md
Documentazione completa del sistema:
- 18 moduli production-ready
- MIDI driver details
- Workflow rules
- Troubleshooting
- Best practices

### 3. Configurazioni
- `config/traktor_midi_mapping.json`
- `DJ_WORKFLOW_RULES.md`
- `requirements.txt`

## 🎯 Best Practices

### ✅ Fai Così

```
"Load a Techno track on deck A"
"Create a new module for X"
"Fix the MIDI timing in browser_navigator"
"Explain how the SYNC logic works"
```

### ❌ Non Fare Così

```
"Riscrivi tutto il progetto"  // Troppo generico
"Cambia tutte le configurazioni"  // Non specifico
```

## 🔍 Debug con Claude Code

Se qualcosa non funziona:

```
"The MIDI connection fails, help me debug"
"Browser navigation is too slow, what can I optimize?"
"Deck A doesn't play after loading, check the workflow"
```

Claude Code:
1. Leggerà i file rilevanti
2. Analizzerà il problema
3. Proporrà soluzioni
4. Modificherà il codice se necessario

## 🆚 Claude Code vs VS Code

### Usa Claude Code quando:
- ✅ Vuoi AI assistance
- ✅ Devi capire codice complesso
- ✅ Vuoi creare nuove funzionalità
- ✅ Hai bisogno di debug assistito

### Usa VS Code quando:
- ✅ Preferisci editing manuale
- ✅ Vuoi più controllo visivo
- ✅ Devi navigare molti file
- ✅ Usi estensioni specifiche

**Puoi usare entrambi!** Apri VS Code in una finestra e Claude Code nel terminale.

## 📝 Note Importanti

### Virtual Environment
Claude Code usa il Python del venv se attivato:
```bash
source activate.sh  # Prima di 'claude'
claude
```

### File Watching
Claude Code vede i cambiamenti ai file in real-time.

### Memoria del Contesto
Claude Code mantiene la conversazione nella sessione corrente, ma ricorda che per nuove sessioni ricaricherà tutto da `claude.md` e skill.

## 🚀 Comandi Quick Reference

```bash
# Setup iniziale
cd /c/traktor
source activate.sh
pip install -r requirements.txt

# Avvia Claude Code
claude

# Test dopo modifiche
python verify_midi_setup.py
python <tuo_script>.py

# Exit Claude Code
exit  # o Ctrl+D
```

---

**Pronto per usare Claude Code! Apri con `claude` e inizia a chiedere! 🤖**
