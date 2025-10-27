"""
AI Client per Autonomous DJ.
Wrapper OpenRouter API per analisi vision e decisioni intelligenti.
"""

import openai
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
from autonomous_dj.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_SITE_URL,
    OPENROUTER_APP_NAME,
    AI_MODEL,
    AI_TEMPERATURE,
    AI_MAX_TOKENS,
    AI_TIMEOUT
)


class DJAIAssistant:
    """
    AI Assistant per decisioni DJ vision-guided.
    Usa OpenRouter + Gemini Flash per analisi screenshot.
    """

    def __init__(self):
        """Inizializza client OpenRouter."""

        # CRITICAL: Non modificare questa configurazione
        self.client = openai.OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
            default_headers={
                "HTTP-Referer": OPENROUTER_SITE_URL,
                "X-Title": OPENROUTER_APP_NAME,
            }
        )

        self.model = AI_MODEL
        self.temperature = AI_TEMPERATURE
        self.max_tokens = AI_MAX_TOKENS
        self.timeout = AI_TIMEOUT

        print(f"[AI] Initialized with model: {self.model}")
        print(f"[AI] Temperature: {self.temperature}")

    def test_connection(self) -> bool:
        """
        Test connessione OpenRouter.

        Returns:
            True se connessione OK, False altrimenti
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Rispondi solo: OK"}
                ],
                max_tokens=10,
                temperature=0
            )

            result = response.choices[0].message.content.strip()
            print(f"[AI] Connection test: {result}")
            return True

        except Exception as e:
            print(f"[AI] Connection FAILED: {e}")
            return False

    def analyze_traktor_screenshot(self, screenshot_path: str) -> Dict:
        """
        Analizza screenshot Traktor e ritorna stato UI completo.

        Args:
            screenshot_path: Path assoluto allo screenshot PNG

        Returns:
            Dict con analisi completa UI:
            {
              "browser": {...},
              "deck_a": {...},
              "deck_b": {...},
              "mixer": {...},
              "recommended_action": {...}
            }
        """
        print(f"\n[AI] Analyzing screenshot: {screenshot_path}")

        # Verifica file esiste
        if not Path(screenshot_path).exists():
            raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

        # Encode immagine base64
        with open(screenshot_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        # Prompt dettagliato per analisi
        prompt = """
Sei un esperto DJ che analizza l'interfaccia di Traktor Pro 3.

Analizza questo screenshot e ritorna un JSON strutturato con:

{
  "browser": {
    "folder_name": "nome della cartella/playlist selezionata nel browser",
    "track_highlighted": "titolo completo della traccia evidenziata (se presente)",
    "track_count_visible": numero di tracce visibili nella lista,
    "scroll_position": "top" | "middle" | "bottom"
  },
  "deck_a": {
    "status": "empty" | "loaded",
    "track_title": "titolo traccia se loaded, altrimenti null",
    "artist": "artista se visibile, altrimenti null",
    "bpm": valore BPM se visibile (number o null),
    "playing": true | false,
    "cue_active": true | false se visibile
  },
  "deck_b": {
    "status": "empty" | "loaded",
    "track_title": "titolo traccia se loaded, altrimenti null",
    "artist": "artista se visibile, altrimenti null",
    "bpm": valore BPM se visibile (number o null),
    "playing": true | false,
    "cue_active": true | false se visibile
  },
  "mixer": {
    "deck_a_volume": "low" | "medium" | "high" (stima visiva dalla posizione fader),
    "deck_b_volume": "low" | "medium" | "high",
    "crossfader": "left" | "center" | "right",
    "warnings": ["lista di warning se volume troppo alto, rischio clipping, etc"]
  },
  "recommended_action": {
    "action": "LOAD_TO_DECK_A" | "LOAD_TO_DECK_B" | "PLAY_DECK_A" | "PLAY_DECK_B" | "STOP_DECK_A" | "STOP_DECK_B" | "SCROLL_BROWSER" | "WAIT",
    "reasoning": "spiegazione chiara del perché questa è l'azione migliore",
    "priority": "high" | "medium" | "low"
  }
}

REGOLE IMPORTANTI:
1. Se una traccia è evidenziata nel browser e un deck è vuoto → raccomanda LOAD_TO_DECK_X
2. Se un deck ha traccia caricata ma non suona → considera PLAY se appropriato
3. Se entrambi i deck sono pieni e uno suona → raccomanda preparazione mix
4. Se tutto è vuoto → raccomanda SCROLL_BROWSER per trovare musica
5. SEMPRE verifica volume Deck B se carichi su Deck A (safety!)

Rispondi SOLO con il JSON, niente altro testo prima o dopo.
"""

        try:
            # Chiamata API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )

            # Estrai risposta
            content = response.choices[0].message.content.strip()

            # Clean markdown se presente
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # Parse JSON
            analysis = json.loads(content)

            print("[AI] Analysis complete:")
            print(f"  Browser: {analysis['browser']['track_highlighted']}")
            print(f"  Deck A: {analysis['deck_a']['status']}")
            print(f"  Deck B: {analysis['deck_b']['status']}")
            print(f"  Action: {analysis['recommended_action']['action']}")

            return analysis

        except json.JSONDecodeError as e:
            print(f"[AI] JSON parsing error: {e}")
            print(f"[AI] Raw response: {content}")
            raise
        except Exception as e:
            print(f"[AI] Analysis error: {e}")
            raise

    def suggest_next_track(
        self,
        current_track: Dict,
        candidates: List[Dict],
        max_candidates: int = 5
    ) -> Dict:
        """
        Suggerisci migliore traccia successiva da lista candidati.

        NOTE: Questo è opzionale - l'algoritmo deterministico è spesso MEGLIO!

        Args:
            current_track: Dict con metadata traccia corrente
            candidates: Lista di dict con tracce candidate (già filtrate da algoritmo)
            max_candidates: Max numero candidati da considerare

        Returns:
            {
              "selected_index": indice nella lista candidates,
              "reasoning": spiegazione scelta,
              "transition_type": "beatmatch" | "cut" | "echo_out" | etc,
              "confidence": 0.0-1.0
            }
        """

        # Limita candidati
        candidates = candidates[:max_candidates]

        # Format prompt
        candidates_text = "\n".join([
            f"{i}. {c['track'].title} by {c['track'].artist} - "
            f"{c['track'].bpm} BPM - Key {c['track'].key} - "
            f"Score: {c['score']:.0f}/100"
            for i, c in enumerate(candidates)
        ])

        prompt = f"""
Sei un DJ esperto. Devi scegliere la prossima traccia per un mix fluido.

TRACCIA CORRENTE:
- {current_track['title']} by {current_track['artist']}
- {current_track['bpm']} BPM
- Key: {current_track['key']}
- Genre: {current_track['genre']}

CANDIDATE (già pre-filtrate per compatibilità):
{candidates_text}

Scegli la MIGLIORE e spiega perché.

Considera:
1. Compatibilità BPM (ideale ±2, accettabile ±5)
2. Armonia (Camelot wheel - transizioni +1/-1 perfette)
3. Energy flow (graduale è meglio di salti bruschi)
4. Genre consistency (mantenere vibe)

Rispondi SOLO con JSON:
{{
  "selected_index": 0,
  "reasoning": "spiegazione dettagliata della scelta",
  "transition_type": "beatmatch",
  "confidence": 0.95
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,  # Leggermente più creativo per suggerimenti
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # Clean markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()

            result = json.loads(content)

            print(f"\n[AI] Track suggestion:")
            print(f"  Selected: #{result['selected_index']}")
            print(f"  Reasoning: {result['reasoning']}")
            print(f"  Confidence: {result['confidence']}")

            return result

        except Exception as e:
            print(f"[AI] Suggestion error: {e}")
            # Fallback: ritorna primo candidato
            return {
                "selected_index": 0,
                "reasoning": "AI error - returning highest scored candidate",
                "transition_type": "beatmatch",
                "confidence": 0.5
            }


# ============================================================================
# TEST RAPIDO
# ============================================================================

if __name__ == "__main__":
    """Test veloce del client AI."""

    print("="*70)
    print("AI CLIENT TEST")
    print("="*70)

    ai = DJAIAssistant()

    # Test 1: Connessione
    print("\nTest 1: Connection")
    if ai.test_connection():
        print("[OK] OpenRouter connection OK")
    else:
        print("[FAIL] Connection FAILED - check API key")
        exit(1)

    # Test 2: Analisi screenshot (se disponibile)
    print("\nTest 2: Screenshot analysis")
    screenshot_dir = Path(r"C:\traktor\data\screenshots")

    if screenshot_dir.exists():
        screenshots = list(screenshot_dir.glob("*.png"))
        if screenshots:
            latest = max(screenshots, key=lambda p: p.stat().st_mtime)
            print(f"Using: {latest.name}")

            try:
                analysis = ai.analyze_traktor_screenshot(str(latest))
                print("\n[OK] Analysis successful!")
                print(json.dumps(analysis, indent=2))
            except Exception as e:
                print(f"[FAIL] Analysis failed: {e}")
        else:
            print("[WARN] No screenshots found - capture one first")
    else:
        print("[WARN] Screenshot directory not found")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
