#!/usr/bin/env python3
"""
Test isolato: solo cattura screenshot multi-screen.
Nessun MIDI, nessuna analisi Claude, solo vision system.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-23
"""
from autonomous_dj.generated.traktor_vision import TraktorVisionSystem
from pathlib import Path


def test_vision_capture():
    """Test base del sistema di cattura."""
    print("=" * 70)
    print("TEST BASIC VISION CAPTURE")
    print("=" * 70)
    print()

    # Init
    print("[1/4] Inizializzando TraktorVisionSystem...")
    try:
        vision = TraktorVisionSystem()
        print("[OK] TraktorVisionSystem inizializzato")
    except Exception as e:
        print(f"[ERROR] Inizializzazione fallita: {e}")
        return False

    # Capture
    print()
    print("[2/4] Catturando screenshot...")
    print("      (Il sistema catturerà TUTTI i monitor automaticamente)")

    try:
        screenshot_path = vision.capture_traktor_window()
        print()
        print(f"[OK] SCREENSHOT SALVATO: {screenshot_path}")

        # Verifica file
        if not Path(screenshot_path).exists():
            print("[ERROR] File non trovato dopo il salvataggio!")
            return False

        # Info file
        print()
        print("[3/4] Verifica file...")
        size_kb = Path(screenshot_path).stat().st_size / 1024
        print(f"      Dimensione: {size_kb:.1f} KB")

        # Info immagine
        try:
            from PIL import Image
            img = Image.open(screenshot_path)
            print(f"      Risoluzione: {img.width}x{img.height} px")
            print(f"      Formato: {img.format}")
            print(f"      Modo colore: {img.mode}")
        except ImportError:
            print("      [WARN] PIL non disponibile per analisi dettagliata")
        except Exception as e:
            print(f"      [WARN] Impossibile analizzare immagine: {e}")

        # Suggerimenti
        print()
        print("[4/4] Verifica manuale richiesta:")
        print(f"      1. Apri: {screenshot_path}")
        print("      2. Verifica che Traktor sia visibile")
        print("      3. Se multi-monitor: controlla che tutti gli schermi siano inclusi")
        print("      4. Verifica qualità e leggibilità del testo")

        return True

    except Exception as e:
        print(f"[ERROR] Cattura fallita: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    success = test_vision_capture()

    print()
    print("=" * 70)
    if success:
        print("[OK] TEST VISION: PASSED")
        print("=" * 70)
        print()
        print("Il sistema di cattura funziona correttamente!")
        print()
        print("Prossimi passi:")
        print("  1. Verifica manualmente lo screenshot")
        print("  2. Se OK, procedi con: python test_midi_only.py")
    else:
        print("[FAIL] TEST VISION: FAILED")
        print("=" * 70)
        print()
        print("Controlla gli errori sopra e risolvi prima di procedere.")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
