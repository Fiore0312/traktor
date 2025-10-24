# VS Code Setup - Virtual Environment

## ✅ Configurazione Completata!

Il progetto è già configurato per usare il virtual environment automaticamente in VS Code.

## Come Funziona

### Apertura Automatica del Virtual Environment

Quando apri il terminale in VS Code nella cartella `C:\traktor`:

1. **VS Code rileva** il file `.vscode/settings.json`
2. **Attiva automaticamente** il virtual environment in `venv/`
3. **Vedrai** `(venv)` nel prompt del terminale

**Esempio di prompt**:
```
(venv) PS C:\traktor>
```

### File di Configurazione

**`.vscode/settings.json`** contiene:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe",
  "python.terminal.activateEnvironment": true,
  ...
}
```

Questo dice a VS Code:
- ✅ Usa Python dal venv
- ✅ Attiva automaticamente il venv nel terminale
- ✅ Configura PYTHONPATH correttamente

## Verifica Setup

### 1. Apri VS Code
```bash
cd C:\traktor
code .
```

### 2. Apri il Terminale
- Premi: `Ctrl + `` (backtick)
- Oppure: Menu → Terminal → New Terminal

### 3. Controlla il Prompt
Dovresti vedere:
```
(venv) PS C:\traktor>
```

Se vedi `(venv)` → ✅ Virtual environment attivo!

### 4. Verifica Python
```bash
python --version
where python
```

Dovresti vedere il path:
```
C:\traktor\venv\Scripts\python.exe
```

## Installazione Dipendenze

Con il venv attivo:

```bash
pip install -r requirements.txt
```

Questo installerà tutte le dipendenze **solo nel virtual environment**, senza toccare il Python di sistema.

## Attivazione Manuale (se necessario)

Se per qualche motivo VS Code non attiva automaticamente il venv:

### Opzione 1: Script Batch
```bash
activate.bat
```

### Opzione 2: Comando Diretto
```bash
venv\Scripts\activate
```

### Opzione 3: PowerShell
```powershell
.\venv\Scripts\Activate.ps1
```

**Nota**: Se PowerShell dà errore "execution policy", esegui:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Disattivazione Virtual Environment

Per uscire dal venv:
```bash
deactivate
```

(Raramente necessario - normalmente lasci il venv attivo mentre lavori)

## Troubleshooting

### VS Code non attiva automaticamente il venv

**Soluzione 1**: Ricarica la finestra
- `Ctrl+Shift+P` → "Developer: Reload Window"

**Soluzione 2**: Seleziona l'interprete manualmente
- `Ctrl+Shift+P` → "Python: Select Interpreter"
- Scegli: `.\venv\Scripts\python.exe`

**Soluzione 3**: Chiudi e riapri VS Code
```bash
# Chiudi VS Code
# Riaprilo con:
code C:\traktor
```

### Il prompt non mostra (venv)

Verifica se il venv è attivo:
```bash
echo $env:VIRTUAL_ENV  # PowerShell
```

Oppure:
```bash
where python
```

Se mostra `C:\traktor\venv\Scripts\python.exe` → È attivo anche se non visibile nel prompt

### Errori durante pip install

**Problema**: "pip is not recognized"
**Soluzione**: Attiva il venv prima:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

**Problema**: Permission denied
**Soluzione**: Esegui VS Code come amministratore (solo per prima installazione)

## Vantaggi del Virtual Environment

✅ **Isolamento**: Dipendenze separate dal sistema
✅ **Riproducibilità**: Stesso ambiente su diversi PC
✅ **Pulizia**: Facile rimuovere tutto (cancella cartella venv/)
✅ **Versioni multiple**: Python diversi per progetti diversi

## Comandi Utili

### Verifica pacchetti installati
```bash
pip list
```

### Aggiorna pip
```bash
python -m pip install --upgrade pip
```

### Reinstalla tutto
```bash
pip install -r requirements.txt --force-reinstall
```

### Salva dipendenze aggiornate
```bash
pip freeze > requirements.txt
```

## File Importanti

- **`venv/`** - Virtual environment (non committare su git!)
- **`.vscode/settings.json`** - Configurazione VS Code (COMMITTATO)
- **`requirements.txt`** - Lista dipendenze (COMMITTATO)
- **`.gitignore`** - Esclude venv/ da git (COMMITTATO)
- **`activate.bat`** - Script attivazione rapida (COMMITTATO)

---

**Tutto pronto! Apri VS Code e il venv si attiverà automaticamente! 🚀**
