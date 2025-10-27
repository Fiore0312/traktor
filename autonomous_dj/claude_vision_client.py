"""
Claude Vision Client per Autonomous DJ.
Usa Anthropic API per analisi screenshot Traktor con massima precisione.
"""

import anthropic
import base64
import json
from pathlib import Path
from typing import Dict, Optional
import time

from autonomous_dj.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_TEMPERATURE,
    CLAUDE_MAX_TOKENS,
    CLAUDE_TIMEOUT
)


class ClaudeVisionClient:
    """
    Client Claude Vision per analisi screenshot Traktor.
    Usa Claude Sonnet 4 con capacità vision avanzate.
    """

    def __init__(self):
        """Inizializza client Anthropic."""

        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "Anthropic API key not configured! "
                "Check ANTHROPIC_API_KEY in config.py"
            )

        # Init client Anthropic
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = CLAUDE_MODEL
        self.temperature = CLAUDE_TEMPERATURE
        self.max_tokens = CLAUDE_MAX_TOKENS
        self.timeout = CLAUDE_TIMEOUT

        print(f"[CLAUDE] Initialized Claude Vision")
        print(f"[CLAUDE] Model: {self.model}")
        print(f"[CLAUDE] Temperature: {self.temperature}")

    def test_connection(self) -> bool:
        """
        Test connessione API Anthropic.

        Returns:
            True se connessione OK, False altrimenti
        """
        print("\n[CLAUDE] Testing API connection...")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=20,
                messages=[
                    {
                        "role": "user",
                        "content": "Rispondi solo con: API OK"
                    }
                ]
            )

            result = response.content[0].text.strip()
            print(f"[CLAUDE] Response: {result}")

            if "OK" in result.upper():
                print("[CLAUDE] [OK] Connection successful!")
                return True
            else:
                print("[CLAUDE] [WARN] Unexpected response")
                return False

        except anthropic.AuthenticationError:
            print("[CLAUDE] [FAIL] Authentication failed - check API key")
            return False
        except anthropic.RateLimitError:
            print("[CLAUDE] [FAIL] Rate limit exceeded")
            return False
        except Exception as e:
            print(f"[CLAUDE] [FAIL] Connection failed: {e}")
            return False

    def analyze_traktor_screenshot(
        self,
        screenshot_path: str,
        verbose: bool = True,
        custom_prompt: Optional[str] = None
    ) -> Dict:
        """
        Analizza screenshot Traktor con Claude Vision.

        Args:
            screenshot_path: Path assoluto screenshot PNG
            custom_prompt: Prompt personalizzato (se None, usa prompt default)
            verbose: Se True, stampa dettagli analisi

        Returns:
            Dict con analisi UI completa
        """

        if verbose:
            print(f"\n[CLAUDE] Analyzing screenshot...")
            print(f"[CLAUDE] File: {Path(screenshot_path).name}")

        # Verifica file esiste
        screenshot_file = Path(screenshot_path)
        if not screenshot_file.exists():
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

        # Carica immagine
        with open(screenshot_file, 'rb') as f:
            image_data = f.read()

        # Encode base64
        image_base64 = base64.standard_b64encode(image_data).decode('utf-8')

        # Determina media type
        media_type = "image/png"
        if screenshot_file.suffix.lower() in ['.jpg', '.jpeg']:
            media_type = "image/jpeg"

        # Use custom prompt if provided, otherwise default
        if custom_prompt:
            analysis_prompt = custom_prompt
        else:
            # Prompt dettagliato per analisi Traktor
            analysis_prompt = """
Sei un esperto DJ che analizza l'interfaccia di Traktor Pro 3.

Analizza questo screenshot molto attentamente e ritorna un JSON strutturato.

STRUTTURA JSON RICHIESTA (copia ESATTAMENTE questa struttura):

{
  "browser": {
    "folder_name": "nome esatto della cartella/playlist selezionata nel browser tree",
    "track_highlighted": "titolo COMPLETO della traccia evidenziata (se presente, altrimenti null)",
    "track_count_visible": numero di tracce visibili nella lista (conta le righe),
    "scroll_position": "top" se all'inizio lista, "middle" se nel mezzo, "bottom" se alla fine
  },
  "deck_a": {
    "status": "empty" se deck vuoto, "loaded" se ha traccia caricata,
    "track_title": "titolo completo traccia se loaded, null se empty",
    "artist": "nome artista se visibile, null altrimenti",
    "bpm": valore numerico BPM se visibile (es: 128.5), null se non visibile,
    "playing": true se waveform si muove/play button attivo, false altrimenti,
    "cue_active": true se cue button illuminato, false altrimenti,
    "position_sec": posizione playhead in secondi se visibile, null altrimenti
  },
  "deck_b": {
    "status": "empty" o "loaded",
    "track_title": "titolo o null",
    "artist": "artista o null",
    "bpm": numero o null,
    "playing": true o false,
    "cue_active": true o false,
    "position_sec": numero o null
  },
  "mixer": {
    "deck_a_volume": "low" (0-30%), "medium" (30-70%), "high" (70-100%) - stima dalla posizione visiva del channel fader,
    "deck_b_volume": "low", "medium", o "high",
    "crossfader": "left" (verso Deck A), "center" (nel mezzo), "right" (verso Deck B),
    "deck_a_gain": "low", "medium", o "high" se gain knob visibile,
    "deck_b_gain": "low", "medium", o "high" se gain knob visibile,
    "warnings": ["lista di warning come 'Deck B volume alto mentre Deck A vuoto', 'Rischio clipping', etc"]
  },
  "ui_state": {
    "focus": "browser" se browser ha focus, "deck_a" se deck A in primo piano, "deck_b", "mixer", "effects",
    "visible_sections": ["browser", "deck_a", "deck_b", "mixer"] - lista sezioni visibili nello screenshot
  },
  "recommended_action": {
    "action": uno tra: "LOAD_TO_DECK_A", "LOAD_TO_DECK_B", "PLAY_DECK_A", "PLAY_DECK_B", "STOP_DECK_A", "STOP_DECK_B", "SCROLL_BROWSER", "CUE_DECK_A", "CUE_DECK_B", "SYNC_DECK_A", "SYNC_DECK_B", "WAIT",
    "reasoning": "spiegazione dettagliata: perché questa azione è la migliore dato lo stato corrente UI",
    "priority": "high" per azioni immediate necessarie, "medium" per azioni consigliate, "low" per ottimizzazioni,
    "safety_check": "OK" se azione è sicura, oppure descrizione warning se ci sono rischi (es: 'Volume Deck B alto')
  }
}

REGOLE CRITICHE DI ANALISI:

1. BROWSER:
   - Se una traccia è EVIDENZIATA (background diverso/selezionata) nel browser → annotala in track_highlighted
   - Se lista è scrollabile, determina posizione scroll guardando scrollbar

2. DECKS:
   - Deck VUOTO = nessuna waveform, area grigia/nera, nessun titolo traccia
   - Deck CARICATO = waveform visibile, titolo traccia mostrato, metadata presenti
   - PLAYING = waveform che si muove, play button illuminato/premuto
   - STOPPED = waveform statica, play button non premuto

3. MIXER:
   - Channel fader GIÙ (bottom) = low volume
   - Channel fader METÀ = medium volume
   - Channel fader SU (top) = high volume
   - Crossfader a SINISTRA = suona più Deck A
   - Crossfader CENTRO = bilanciato
   - Crossfader a DESTRA = suona più Deck B

4. AZIONI RACCOMANDATE:
   - Se traccia evidenziata + Deck A vuoto → LOAD_TO_DECK_A (priority: high)
   - Se traccia evidenziata + Deck B vuoto → LOAD_TO_DECK_B (priority: high)
   - Se Deck ha traccia + non playing → considera PLAY_DECK_X (priority: medium)
   - Se entrambi deck pieni + uno suona → WAIT o preparazione mix (priority: low)
   - Se tutto vuoto → SCROLL_BROWSER per trovare musica (priority: high)

5. SAFETY:
   - SEMPRE verifica volume Deck opposto quando raccomandi LOAD
   - SEMPRE avvisa se volume Deck B alto mentre carichi su Deck A (rischio audio inaspettato)
   - SEMPRE nota se ci sono rischi di clipping (entrambi volumi alti + crossfader centro)

Rispondi SOLO con il JSON valido. Niente testo prima o dopo. Nessun markdown.
"""

        try:
            # Timestamp per tracking
            start_time = time.time()

            # Chiamata API Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": analysis_prompt
                            }
                        ]
                    }
                ]
            )

            elapsed = time.time() - start_time

            # Estrai testo risposta
            response_text = response.content[0].text.strip()

            # Clean markdown se presente
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            # Parse JSON
            analysis = json.loads(response_text)

            # Log risultati
            if verbose:
                print(f"[CLAUDE] Analysis complete ({elapsed:.1f}s)")
                print(f"[CLAUDE] Browser: {analysis['browser']['track_highlighted']}")
                print(f"[CLAUDE] Deck A: {analysis['deck_a']['status']}")
                print(f"[CLAUDE] Deck B: {analysis['deck_b']['status']}")
                print(f"[CLAUDE] Action: {analysis['recommended_action']['action']}")
                print(f"[CLAUDE] Reasoning: {analysis['recommended_action']['reasoning']}")

                if analysis['mixer']['warnings']:
                    print(f"[CLAUDE] [WARN] Warnings: {', '.join(analysis['mixer']['warnings'])}")

            # Add metadata
            analysis['_metadata'] = {
                'timestamp': time.time(),
                'elapsed_seconds': elapsed,
                'model': self.model,
                'screenshot_file': str(screenshot_file.name)
            }

            return analysis

        except json.JSONDecodeError as e:
            print(f"[CLAUDE] [FAIL] JSON parsing error: {e}")
            print(f"[CLAUDE] Raw response (first 500 chars):")
            print(response_text[:500])
            raise

        except anthropic.APIError as e:
            print(f"[CLAUDE] [FAIL] API Error: {e}")
            raise

        except Exception as e:
            print(f"[CLAUDE] [FAIL] Unexpected error: {e}")
            raise

    def get_usage_info(self) -> Dict:
        """
        Ritorna informazioni sull'uso API (se disponibili).

        Returns:
            Dict con statistiche uso
        """
        # Note: Anthropic API non espone facilmente usage stats
        # Questo è placeholder per future implementazioni
        return {
            "model": self.model,
            "note": "Check console.anthropic.com for detailed usage stats"
        }


# ============================================================================
# TEST STANDALONE
# ============================================================================

if __name__ == "__main__":
    """Test veloce del client Claude Vision."""

    print("="*70)
    print("CLAUDE VISION CLIENT TEST")
    print("="*70)

    # Init client
    try:
        client = ClaudeVisionClient()
    except Exception as e:
        print(f"\n[FAIL] Initialization failed: {e}")
        exit(1)

    # Test 1: Connection
    print("\nTEST 1: API Connection")
    print("-"*70)
    if not client.test_connection():
        print("\n[FAIL] Connection test FAILED")
        print("Check:")
        print("  - API key in config.py is correct")
        print("  - Internet connection working")
        print("  - Anthropic API status: https://status.anthropic.com")
        exit(1)

    # Test 2: Screenshot analysis
    print("\nTEST 2: Screenshot Analysis")
    print("-"*70)

    screenshot_dir = Path(r"C:\traktor\data\screenshots")
    if not screenshot_dir.exists():
        print("[WARN] Screenshot directory not found")
        print(f"   Expected: {screenshot_dir}")
        print("   Create screenshot first with: python test_basic_vision.py")
        exit(0)

    screenshots = list(screenshot_dir.glob("*.png"))
    if not screenshots:
        print("[WARN] No screenshots available")
        print("   Create one with: python test_basic_vision.py")
        exit(0)

    # Usa screenshot più recente
    latest_screenshot = max(screenshots, key=lambda p: p.stat().st_mtime)
    print(f"Using: {latest_screenshot.name}")

    try:
        analysis = client.analyze_traktor_screenshot(
            str(latest_screenshot),
            verbose=True
        )

        print("\n" + "="*70)
        print("[OK] ANALYSIS SUCCESSFUL")
        print("="*70)

        # Save analysis JSON
        output_file = latest_screenshot.parent / f"{latest_screenshot.stem}_claude_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"\n[SAVED] Full analysis saved: {output_file}")

        # Pretty print key findings
        print("\n[INFO] KEY FINDINGS:")
        print(f"  Browser folder: {analysis['browser']['folder_name']}")
        print(f"  Track highlighted: {analysis['browser']['track_highlighted']}")
        print(f"  Deck A: {analysis['deck_a']['status']}")
        if analysis['deck_a']['status'] == 'loaded':
            print(f"    -> {analysis['deck_a']['track_title']}")
            print(f"    -> Playing: {analysis['deck_a']['playing']}")
        print(f"  Deck B: {analysis['deck_b']['status']}")
        if analysis['deck_b']['status'] == 'loaded':
            print(f"    -> {analysis['deck_b']['track_title']}")
            print(f"    -> Playing: {analysis['deck_b']['playing']}")

        print(f"\n[INFO] RECOMMENDATION:")
        print(f"  Action: {analysis['recommended_action']['action']}")
        print(f"  Priority: {analysis['recommended_action']['priority']}")
        print(f"  Reasoning: {analysis['recommended_action']['reasoning']}")
        print(f"  Safety: {analysis['recommended_action']['safety_check']}")

        if analysis['mixer']['warnings']:
            print(f"\n[WARN] WARNINGS:")
            for warning in analysis['mixer']['warnings']:
                print(f"  - {warning}")

    except Exception as e:
        print(f"\n[FAIL] Analysis FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

    print("\n" + "="*70)
    print("[OK] ALL TESTS PASSED")
    print("="*70)
    print("\nClaude Vision is ready for autonomous DJ workflow!")
    print("\n")
