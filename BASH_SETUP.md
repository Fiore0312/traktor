# Git Bash Setup - Virtual Environment

## ✅ Come Attivare il Virtual Environment in Git Bash

### Metodo 1: Script Automatico (CONSIGLIATO)

```bash
cd /c/traktor
source activate.sh
```

Vedrai:
```
Activating virtual environment...

Virtual environment activated!
Python location: /c/traktor/venv
```

### Metodo 2: Comando Diretto

```bash
source venv/Scripts/activate
```

**IMPORTANTE**: Usa `/` (slash) NON `\` (backslash) in Git Bash!

### Metodo 3: Punto + Spazio (shorthand)

```bash
. venv/Scripts/activate
```

Il `.` è equivalente a `source` in Bash.

## ✅ Verifica Attivazione

Dopo l'attivazione, il tuo prompt cambierà in:

```bash
(venv) Utente@DESKTOP-QJ6NQ9E MINGW64 /c/traktor
$
```

Se vedi `(venv)` → ✅ Virtual environment attivo!

### Comandi di Verifica

```bash
# Controlla Python path
which python
# Output: /c/traktor/venv/Scripts/python

# Controlla versione
python --version

# Controlla variabile VIRTUAL_ENV
echo $VIRTUAL_ENV
# Output: /c/traktor/venv
```

## 📋 Setup Completo in Git Bash

```bash
# 1. Vai nella cartella progetto
cd /c/traktor

# 2. Attiva virtual environment
source activate.sh
# Oppure: source venv/Scripts/activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Verifica setup MIDI
python verify_midi_setup.py
```

## 🔧 VS Code + Git Bash

### Configurazione Automatica

Ho aggiornato `.vscode/settings.json` per:
- ✅ Usare Git Bash come terminale default
- ✅ Attivare automaticamente il venv

**IMPORTANTE**: Devi chiudere VS Code COMPLETAMENTE e riaprirlo:

```bash
# Chiudi tutte le finestre VS Code
# Poi riapri:
cd /c/traktor
code .
```

### Test Apertura Terminale

1. Apri VS Code in `/c/traktor`
2. Apri terminale: `Ctrl + `` (backtick)
3. Dovresti vedere automaticamente:
   ```bash
   (venv) Utente@DESKTOP-QJ6NQ9E MINGW64 /c/traktor
   $
   ```

### Se Non Si Attiva Automaticamente

Potrebbe essere un bug di VS Code con Git Bash. Soluzione:

**Crea file `.bashrc` nella home**:

```bash
# Vai nella home
cd ~

# Crea/modifica .bashrc
nano .bashrc
```

Aggiungi questa riga:
```bash
# Auto-activate venv in /c/traktor
if [[ "$PWD" == /c/traktor* ]] && [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -f /c/traktor/venv/Scripts/activate ]]; then
        source /c/traktor/venv/Scripts/activate
    fi
fi
```

Salva e ricarica:
```bash
source ~/.bashrc
```

## 🚨 Errori Comuni e Soluzioni

### Errore: "activate.bat: command not found"

**Problema**: `.bat` è per Windows CMD/PowerShell, non Bash

**Soluzione**: Usa `activate.sh` o `source venv/Scripts/activate`

```bash
# ❌ Non funziona in Bash:
activate.bat

# ✅ Funziona in Bash:
source activate.sh
# Oppure:
source venv/Scripts/activate
```

### Errore: "venv/scripts\activate: No such file"

**Problema**: Backslash `\` è escape character in Bash

**Soluzione**: Usa forward slash `/`

```bash
# ❌ Non funziona:
venv/scripts\activate

# ✅ Funziona:
source venv/Scripts/activate
```

### Errore: "Permission denied"

**Soluzione**: Aggiungi `source` o `.` prima:

```bash
# ❌ Non funziona:
venv/Scripts/activate

# ✅ Funziona:
source venv/Scripts/activate
```

### VS Code non attiva automaticamente

**Soluzione 1**: Ricarica finestra
- `Ctrl+Shift+P`
- "Developer: Reload Window"

**Soluzione 2**: Aggiungi al `.bashrc` (vedi sopra)

**Soluzione 3**: Attiva manualmente nel terminale:
```bash
source venv/Scripts/activate
```

## 📝 Script Utili per Git Bash

### activate.sh (già creato)

```bash
source activate.sh
```

### Crea alias permanente

Aggiungi al `~/.bashrc`:

```bash
# Alias per attivare venv traktor
alias traktor='cd /c/traktor && source venv/Scripts/activate'
```

Poi puoi fare:
```bash
traktor
# Ti porta in /c/traktor con venv attivo!
```

## 🎯 Workflow Completo

### Ogni volta che lavori:

```bash
# 1. Apri Git Bash
# 2. Vai nel progetto
cd /c/traktor

# 3. Attiva venv
source activate.sh

# 4. Lavora normalmente
python verify_midi_setup.py
pip list
python autonomous_dj/live_performer.py
# etc...
```

### In VS Code:

```bash
# 1. Apri VS Code
cd /c/traktor
code .

# 2. Apri terminale (Ctrl+`)
# Se non si attiva automaticamente:
source venv/Scripts/activate

# 3. Lavora normalmente
```

## 🔍 Debug Attivazione

### Check 1: File esiste?

```bash
ls -la venv/Scripts/activate
# Deve mostrare il file
```

### Check 2: File è eseguibile?

```bash
file venv/Scripts/activate
# Output: ASCII text executable
```

### Check 3: Contenuto corretto?

```bash
head -5 venv/Scripts/activate
# Deve iniziare con: #!/bin/sh
```

### Check 4: Path corretto?

```bash
pwd
# Deve essere: /c/traktor
```

## 💡 Pro Tips

### 1. Usa Tab Completion

```bash
source venv/Sc<TAB>  # Autocompleta a Scripts/
source venv/Scripts/ac<TAB>  # Autocompleta a activate
```

### 2. Disattiva quando hai finito

```bash
deactivate
# Torna al Python di sistema
```

### 3. Verifica sempre prima di pip install

```bash
which pip
# Deve mostrare: /c/traktor/venv/Scripts/pip
```

Se mostra altro path → venv NON attivo!

## 📚 Comandi Quick Reference

```bash
# Attivazione
source venv/Scripts/activate

# Verifica
which python
echo $VIRTUAL_ENV

# Installa dipendenze
pip install -r requirements.txt

# Disattivazione
deactivate

# Script automatico
source activate.sh
```

## ✅ Checklist Setup Iniziale

- [ ] Vai in `/c/traktor`
- [ ] Esegui `source activate.sh`
- [ ] Vedi `(venv)` nel prompt
- [ ] Esegui `pip install -r requirements.txt`
- [ ] Esegui `python verify_midi_setup.py`

---

**Pronto! Ora il venv funziona perfettamente in Git Bash! 🚀**
