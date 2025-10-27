# 📚 Traktor AI - Documentazione Completa

Benvenuto nella documentazione ufficiale di **Traktor AI**, il sistema DJ autonomo con intelligenza artificiale.

---

## 🗺️ Navigazione Rapida

### 🚀 Per Iniziare

Sei nuovo? Parti da qui:

1. **[README principale](../README.md)** - Panoramica del progetto e quick start
2. **[SETUP.md](SETUP.md)** - Installazione e configurazione dettagliata
3. **[Primo utilizzo](#primo-utilizzo)** - Guida step-by-step

### 📖 Guide Tecniche

Approfondisci il sistema:

- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Come funziona l'integrazione completa
- **[VISION_GUIDE.md](VISION_GUIDE.md)** - Vision mode vs Blind mode, costi e setup
- **[CAMELOT_WHEEL_GUIDE.md](CAMELOT_WHEEL_GUIDE.md)** - Teoria harmonic mixing
- **[API_REFERENCE.md](API_REFERENCE.md)** - Documentazione API REST e WebSocket

### 🔧 Risoluzione Problemi

Qualcosa non funziona?

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Soluzioni ai problemi più comuni

### 💻 Sviluppatori

Vuoi contribuire?

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guida per sviluppatori e contributori

---

## 🎯 Primo Utilizzo

### Prerequisiti (5 minuti)

```bash
# 1. Verifica Python
python --version  # Deve essere 3.8+

# 2. Clona repository
git clone https://github.com/Fiore0312/traktor.git
cd traktor

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura MIDI
# Windows: Apri loopMIDI, crea porta "Traktor MIDI Bus 1"
# macOS: Audio MIDI Setup → IAC Driver → Enable
```

### Setup Traktor (10 minuti)

```bash
# 1. Apri Traktor Pro 3

# 2. Analizza keys
# Browser → Select All → Right-click → Analyze → Determine Key

# 3. Importa TSI mapping
# Preferences → Controller Manager → Import
# Seleziona: config/TraktorMIDIMapping.tsi

# 4. Set Interaction Mode to "Direct"
# Preferences → Controller Manager → Generic MIDI → "Direct"
```

### Prima Esecuzione (2 minuti)

```bash
# 1. Parse collection
python collection_parser_xml.py

# 2. Avvia server
START_SERVER_PRODUCTION.bat  # Windows
# oppure
python autonomous_dj/workflow_controller.py  # macOS/Linux

# 3. Apri browser
# http://localhost:8000

# 4. Prova primo comando
# Click "🎧 Auto-Select Compatible"
```

**Done!** Il sistema è pronto. ✅

---

## 📑 Struttura Documentazione

```
docs/
├── README.md                    # Questo file (indice)
│
├── SETUP.md                     # Setup dettagliato
│   ├── Requisiti sistema
│   ├── Installazione software
│   ├── Configurazione Traktor
│   ├── Setup MIDI
│   ├── Configurazione API keys
│   └── Verifica setup
│
├── INTEGRATION_GUIDE.md         # Architettura e integrazione
│   ├── Panoramica architettura
│   ├── Data flow diagrams
│   ├── Componenti core
│   ├── Workflow end-to-end
│   ├── OpenRouter + Vision integration
│   ├── MIDI communication layer
│   ├── Camelot Wheel integration
│   ├── Safety checks system
│   └── Database layer
│
├── VISION_GUIDE.md              # Sistema Vision
│   ├── Blind mode vs Vision mode
│   ├── Configurazione Vision API
│   ├── Costi e budget
│   ├── Troubleshooting Vision
│   └── Best practices
│
├── CAMELOT_WHEEL_GUIDE.md       # Harmonic mixing
│   ├── Teoria Camelot Wheel
│   ├── Compatibility rules
│   ├── Algoritmo matching
│   ├── BPM matching
│   ├── Scoring system
│   └── DJ workflow tips
│
├── API_REFERENCE.md             # API documentation
│   ├── REST endpoints
│   ├── WebSocket API
│   ├── Request/response formats
│   ├── Error codes
│   └── Testing examples
│
├── TROUBLESHOOTING.md           # Risoluzione problemi
│   ├── MIDI non funziona
│   ├── Vision API errors
│   ├── Collection non trovata
│   ├── Server non si avvia
│   ├── Track selection fails
│   ├── Performance issues
│   ├── Traktor non risponde
│   └── Database corruption
│
└── DEVELOPMENT.md               # Guida sviluppatori
    ├── Development setup
    ├── Project structure
    ├── Code style
    ├── Testing
    ├── Adding features
    ├── MIDI mappings
    ├── Database schema
    ├── API development
    └── Contributing guidelines
```

---

## 🎓 Learning Path

### Beginner

1. **Leggi**: [README principale](../README.md)
2. **Setup**: Segui [SETUP.md](SETUP.md) passo-passo
3. **Test**: Prova comandi base nella web UI
4. **Impara**: Leggi [CAMELOT_WHEEL_GUIDE.md](CAMELOT_WHEEL_GUIDE.md) per capire harmonic mixing

### Intermediate

1. **Esplora**: [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) per capire architettura
2. **Vision**: Leggi [VISION_GUIDE.md](VISION_GUIDE.md) e decidi se usare Vision mode
3. **API**: Prova gli endpoints in [API_REFERENCE.md](API_REFERENCE.md)
4. **Troubleshoot**: Risolvi problemi con [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Advanced

1. **Develop**: Studia [DEVELOPMENT.md](DEVELOPMENT.md)
2. **Contribuisci**: Aggiungi features o fix bugs
3. **Customizza**: Modifica MIDI mappings per il tuo workflow
4. **Ottimizza**: Tuning performance e caching

---

## 📊 Quick Reference

### Comandi Utili

```bash
# Verifica MIDI
python verify_midi_setup.py

# Parse collection
python collection_parser_xml.py

# Test integration
python test_intelligent_integration.py

# Avvia server
START_SERVER_PRODUCTION.bat

# Check logs
tail -f data/logs/traktor_ai.log
```

### API Endpoints Principali

```bash
# Chat command
POST http://localhost:8000/api/chat
{"message": "trova traccia compatibile"}

# Auto-select
POST http://localhost:8000/api/auto-select-track
{"deck": "B"}

# System status
GET http://localhost:8000/api/status

# Compatible tracks
GET http://localhost:8000/api/compatible-tracks?key=8A&bpm=128
```

### File di Configurazione

```
autonomous_dj/config.py          # API keys (NON in git!)
config/traktor_midi_mapping.json # MIDI CC mappings
config/TraktorMIDIMapping.tsi    # Traktor TSI file
tracks.db                        # SQLite database
```

---

## 🔗 Link Utili

### External Resources

- **Traktor Pro 3**: https://www.native-instruments.com/en/products/traktor/
- **OpenRouter API**: https://openrouter.ai/
- **Anthropic Claude**: https://console.anthropic.com/
- **Camelot Wheel**: https://mixedinkey.com/harmonic-mixing-guide/
- **loopMIDI**: https://www.tobias-erichsen.de/software/loopmidi.html

### Project Links

- **GitHub Repository**: https://github.com/Fiore0312/traktor
- **Issues**: https://github.com/Fiore0312/traktor/issues
- **Discussions**: https://github.com/Fiore0312/traktor/discussions

---

## 📞 Supporto

### Community Support

- **GitHub Issues**: Per bug reports e feature requests
- **GitHub Discussions**: Per domande generali e discussioni
- **Email**: [your-email@example.com]

### Documentazione Aggiuntiva

- **CLAUDE.md**: Context per Claude Code (AI assistant)
- **DJ_WORKFLOW_RULES.md**: Best practices DJ professionali
- **MIDI_INTERACTION_MODE_FIX.md**: Critical MIDI setup
- **README_INTEGRATION_COMPLETE.md**: Integration success summary

---

## 🎉 Contributors

Grazie a tutti coloro che hanno contribuito a questo progetto!

**Main Developer**: DJ Fiore
**AI Assistance**: Claude (Anthropic)
**Community**: [Lista contributors]

---

## 📄 License

Questo progetto è rilasciato sotto licenza MIT. Vedi [LICENSE](../LICENSE) per dettagli.

---

**Made with ❤️ for the DJ community**

*Last updated: October 26, 2025*
