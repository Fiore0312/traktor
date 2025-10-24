# Installazione Tesseract OCR per Windows

## Download

Scarica Tesseract OCR da:
https://github.com/UB-Mannheim/tesseract/wiki

**File consigliato**: `tesseract-ocr-w64-setup-5.x.x.exe`

## Installazione

1. Esegui l'installer
2. **IMPORTANTE**: Durante l'installazione, seleziona "Add to PATH"
3. Installa in: `C:\Program Files\Tesseract-OCR` (default)

## Configurazione Python

Dopo l'installazione, configura il path in Python:

```python
import pytesseract

# Imposta il path di tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Verifica Installazione

```bash
tesseract --version
```

Dovrebbe mostrare: `tesseract 5.x.x`

## Alternative

Se non vuoi installare Tesseract, possiamo usare:
- **EasyOCR** (no dependencies esterne)
- **Claude Vision API** (uso Claude stesso per OCR)

Quale preferisci?
