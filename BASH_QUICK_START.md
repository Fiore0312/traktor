# 🚀 QUICK START - Git Bash

## Attivazione Virtual Environment

```bash
cd /c/traktor
source activate.sh
```

Dovresti vedere:
```bash
(venv) Utente@DESKTOP-QJ6NQ9E MINGW64 /c/traktor
$
```

## Prima Volta - Setup Completo

```bash
# 1. Vai nel progetto
cd /c/traktor

# 2. Attiva venv
source activate.sh

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Verifica MIDI
python verify_midi_setup.py
```

## Comandi Utili

```bash
# Attiva venv
source activate.sh

# Verifica Python
which python          # Deve mostrare: /c/traktor/venv/Scripts/python

# Verifica venv attivo
echo $VIRTUAL_ENV     # Deve mostrare: /c/traktor/venv

# Disattiva venv
deactivate

# Lista pacchetti installati
pip list

# Installa singolo pacchetto
pip install <nome-pacchetto>
```

## Claude Code vs VS Code

**Claude Code** (AI assistant nel terminale):
```bash
cd /c/traktor
claude
```

**VS Code** (editor normale):
```bash
cd /c/traktor
code .
```

Per questo progetto, probabilmente vuoi usare **`claude`** (Claude Code)!

## Troubleshooting

### "activate.bat: command not found"
❌ `.bat` non funziona in Git Bash
✅ Usa: `source activate.sh`

### "venv/scripts\activate: No such file"
❌ Backslash `\` non funziona in Bash
✅ Usa: `source venv/Scripts/activate` (con `/`)

### VS Code non attiva automaticamente
✅ Vedi `BASH_SETUP.md` sezione "Se Non Si Attiva Automaticamente"

## Documentazione

- **BASH_SETUP.md** - Guida completa Git Bash + troubleshooting
- **START_HERE.md** - Guida generale progetto
- **SETUP_COMPLETE.md** - Checklist finale

---

**🎵 Happy DJ-ing! 🤖**
