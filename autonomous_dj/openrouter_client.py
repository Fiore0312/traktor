"""
OpenRouter LLM Client - Free AI for natural language command parsing.

Uses OpenRouter's free models (Gemini 2.0 Flash) for intelligent chat.
"""

import os
import json
from typing import Dict, Optional, List
import requests
from requests.exceptions import RequestException


class OpenRouterClient:
    """
    Client per interagire con OpenRouter API (modelli LLM gratuiti).
    Usato per parsing intelligente dei comandi utente.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "deepseek/deepseek-chat",
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: int = 30
    ):
        """
        Inizializza client OpenRouter.

        Args:
            api_key: OpenRouter API key (or from config)
            model: Model to use (default: free Gemini 2.0)
            base_url: OpenRouter API base URL
            timeout: Request timeout in seconds
        """
        # Try to get API key from config if not provided
        if not api_key:
            try:
                from autonomous_dj.config import OPENROUTER_API_KEY
                api_key = OPENROUTER_API_KEY
            except ImportError:
                pass

        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = timeout

        # Conversation history (for context)
        self.conversation_history: List[Dict] = []

        print(f"[OPENROUTER] Initialized with model: {model}")
        if not self.api_key or self.api_key == "your-openrouter-api-key-here":
            print("[OPENROUTER] WARNING: API key not configured. Using fallback mode.")

    def parse_dj_command(self, user_input: str) -> Dict:
        """
        Parse comando DJ usando LLM.

        Args:
            user_input: Richiesta utente in linguaggio naturale

        Returns:
            Structured action plan:
            {
                'action': 'LOAD_TRACK' | 'PLAY_DECK' | 'PAUSE_DECK' | 'GET_STATUS' | 'START_AUTONOMOUS' | 'MIX_TRANSITION' | 'ADJUST_EQ' | 'SYNC_DECKS',
                'deck': 'A' | 'B' | None,
                'genre': str | None,
                'bpm_range': [min, max] | None,
                'energy_level': 'low' | 'medium' | 'high' | None,
                'confidence': float  # 0-1
            }
        """

        if not self.api_key or self.api_key == "your-openrouter-api-key-here":
            print("[OPENROUTER] No API key, using fallback parsing")
            return self._fallback_parse(user_input)

        system_prompt = """You are a DJ assistant AI that parses user commands into structured actions for Traktor Pro 3.

Available actions:
- LOAD_TRACK: Load a track on a deck
- PLAY_DECK: Start playing a deck
- PAUSE_DECK: Stop/pause a deck
- GET_STATUS: Show current system status
- START_AUTONOMOUS: Enable autonomous DJ mode
- NAVIGATE_FOLDER: Navigate to a folder in browser (e.g., 'dub', 'techno')
- NAVIGATE_AND_PLAY: Navigate to folder AND load+play a track (compound action)
- FIND_COMPATIBLE_TRACK: Find and load a harmonically compatible track (uses Camelot Wheel + BPM matching)
- MIX_TRANSITION: Mix between two decks
- ADJUST_EQ: Adjust EQ controls
- SYNC_DECKS: Sync BPM between decks

Available decks: A, B

Music genres: dub, techno, house, trance, dnb, dubstep, ambient, breaks

Energy levels: low, medium, high

Respond ONLY with valid JSON matching this schema:
{
    "action": "ACTION_NAME",
    "deck": "A or B or null",
    "folder": "folder name or null (for NAVIGATE_FOLDER)",
    "genre": "genre name or null",
    "bpm_range": [min, max] or null,
    "energy_level": "low/medium/high or null",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}

Examples:
User: "Load a Techno track on Deck A"
{"action": "LOAD_TRACK", "deck": "A", "genre": "techno", "bpm_range": null, "energy_level": null, "confidence": 0.95, "reasoning": "Clear load command with deck and genre"}

User: "Play something energetic on the left deck"
{"action": "LOAD_TRACK", "deck": "A", "genre": null, "bpm_range": [128, 140], "energy_level": "high", "confidence": 0.85, "reasoning": "Left deck is A, energetic suggests high BPM"}

User: "What's playing?"
{"action": "GET_STATUS", "deck": null, "genre": null, "bpm_range": null, "energy_level": null, "confidence": 1.0, "reasoning": "Status query"}


User: "Navigate to the dub folder"
{"action": "NAVIGATE_FOLDER", "deck": null, "folder": "dub", "genre": null, "bpm_range": null, "energy_level": null, "confidence": 0.95, "reasoning": "Clear navigation command to dub folder"}

User: "vai alla cartella dub e suona una traccia"
{"action": "NAVIGATE_AND_PLAY", "deck": "A", "folder": "dub", "genre": null, "bpm_range": null, "energy_level": null, "confidence": 0.95, "reasoning": "Navigate to dub folder and play a track - compound action"}

User: "Find a compatible track for Deck A"
{"action": "FIND_COMPATIBLE_TRACK", "deck": "B", "genre": null, "bpm_range": null, "energy_level": null, "confidence": 0.9, "reasoning": "Smart matching request - will analyze Deck A and find compatible track for Deck B"}

User: "Mix the tracks" or "Mixale" or "Do a transition"
{"action": "MIX_TRANSITION", "deck": null, "genre": null, "bpm_range": null, "energy_level": null, "confidence": 0.95, "reasoning": "User wants to mix/transition between the two decks"}

User: "Start the AI DJ"
{"action": "START_AUTONOMOUS", "deck": null, "genre": null, "bpm_range": null, "energy_level": null, "confidence": 0.9, "reasoning": "Request for autonomous mode"}"""

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/Fiore0312/traktor",
                    "X-Title": "Traktor DJ AI"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            # Extract LLM response
            llm_response = data['choices'][0]['message']['content'].strip()

            # Parse JSON response
            # Remove markdown code blocks if present
            if llm_response.startswith("```"):
                llm_response = llm_response.split("```")[1]
                if llm_response.startswith("json"):
                    llm_response = llm_response[4:]
                llm_response = llm_response.strip()

            parsed = json.loads(llm_response)

            print(f"[OPENROUTER] Parsed command: {parsed}")

            return {
                'action': parsed.get('action', 'GET_STATUS'),
                'deck': parsed.get('deck'),
                'folder': parsed.get('folder'),
                'genre': parsed.get('genre'),
                'bpm_range': parsed.get('bpm_range'),
                'energy_level': parsed.get('energy_level'),
                'confidence': parsed.get('confidence', 0.5),
                'reasoning': parsed.get('reasoning', '')
            }

        except RequestException as e:
            print(f"[OPENROUTER] API error: {e}")
            return self._fallback_parse(user_input)
        except json.JSONDecodeError as e:
            print(f"[OPENROUTER] JSON parse error: {e}")
            return self._fallback_parse(user_input)
        except Exception as e:
            print(f"[OPENROUTER] Unexpected error: {e}")
            return self._fallback_parse(user_input)

    def _fallback_parse(self, user_input: str) -> Dict:
        """
        Fallback parsing con regole semplici (quando API non disponibile).
        """
        cmd_lower = user_input.lower()

        # Load commands
        if 'carica' in cmd_lower or 'load' in cmd_lower:
            deck = 'A' if 'deck a' in cmd_lower or ' a' in cmd_lower else 'B'
            genre = self._extract_genre(cmd_lower)
            return {
                'action': 'LOAD_TRACK',
                'deck': deck,
                'genre': genre,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.7,
                'reasoning': 'Fallback rule-based parsing'
            }

        # Play commands
        if 'play' in cmd_lower or 'parti' in cmd_lower or 'suona' in cmd_lower:
            deck = 'A' if 'deck a' in cmd_lower or ' a' in cmd_lower else 'B'
            return {
                'action': 'PLAY_DECK',
                'deck': deck,
                'genre': None,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.8,
                'reasoning': 'Fallback rule-based parsing'
            }

        # Pause commands
        if 'pause' in cmd_lower or 'ferma' in cmd_lower or 'stop' in cmd_lower:
            deck = 'A' if 'deck a' in cmd_lower or ' a' in cmd_lower else 'B'
            return {
                'action': 'PAUSE_DECK',
                'deck': deck,
                'genre': None,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.8,
                'reasoning': 'Fallback rule-based parsing'
            }

        # Status query
        if 'stato' in cmd_lower or 'status' in cmd_lower or 'cosa' in cmd_lower:
            return {
                'action': 'GET_STATUS',
                'deck': None,
                'genre': None,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.9,
                'reasoning': 'Fallback rule-based parsing'
            }

        # Autonomous mode
        if 'automatico' in cmd_lower or 'autonomo' in cmd_lower or 'autonomous' in cmd_lower:
            return {
                'action': 'START_AUTONOMOUS',
                'deck': None,
                'genre': None,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.85,
                'reasoning': 'Fallback rule-based parsing'
            }

        # Find compatible track
        if ('compatib' in cmd_lower or 'trova' in cmd_lower or 'find' in cmd_lower) and ('traccia' in cmd_lower or 'track' in cmd_lower):
            # Target deck is the one NOT playing (if A is playing, load to B and vice versa)
            deck = 'B' if 'deck a' in cmd_lower or ' a' in cmd_lower else 'A'
            return {
                'action': 'FIND_COMPATIBLE_TRACK',
                'deck': deck,
                'genre': None,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.8,
                'reasoning': 'Fallback rule-based parsing for compatible track search'
            }

        # Mix/transition commands
        if any(word in cmd_lower for word in ['mix', 'mixa', 'mixale', 'transition', 'transizione', 'crossfade', 'fade']):
            return {
                'action': 'MIX_TRANSITION',
                'deck': None,  # Will auto-detect source/target
                'genre': None,
                'bpm_range': None,
                'energy_level': None,
                'confidence': 0.85,
                'reasoning': 'Fallback rule-based parsing for mix transition'
            }

        # Unknown command
        return {
            'action': 'GET_STATUS',
            'deck': None,
            'genre': None,
            'bpm_range': None,
            'energy_level': None,
            'confidence': 0.3,
            'reasoning': 'Command not understood, defaulting to status'
        }

    def _extract_genre(self, text: str) -> Optional[str]:
        """Estrai genere da testo."""
        genres = ['dub', 'techno', 'house', 'trance', 'dnb', 'dubstep', 'ambient', 'breaks']
        for genre in genres:
            if genre in text:
                return genre
        return None

    def chat(self, user_message: str, system_context: Optional[str] = None) -> str:
        """
        Chat generale con LLM (per risposte conversazionali).

        Args:
            user_message: Messaggio utente
            system_context: Context aggiuntivo (stato Traktor, etc)

        Returns:
            Risposta LLM
        """

        if not self.api_key or self.api_key == "your-openrouter-api-key-here":
            return "OpenRouter API key not configured. Using rule-based responses."

        system_prompt = """You are a friendly DJ assistant AI helping control Traktor Pro 3.

Be concise, helpful, and DJ-focused. Use music terminology appropriately.
When confirming actions, be brief but clear."""

        if system_context:
            system_prompt += f"\n\nCurrent Traktor state:\n{system_context}"

        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            messages = [{"role": "system", "content": system_prompt}] + self.conversation_history

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/Fiore0312/traktor",
                    "X-Title": "Traktor DJ AI"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 300
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()

            llm_reply = data['choices'][0]['message']['content'].strip()

            # Add to history
            self.conversation_history.append({"role": "assistant", "content": llm_reply})

            # Keep history manageable (last 10 messages)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return llm_reply

        except Exception as e:
            print(f"[OPENROUTER] Chat error: {e}")
            return "I'm having trouble connecting to the AI service right now."

    def clear_history(self):
        """Cancella cronologia conversazione."""
        self.conversation_history = []
        print("[OPENROUTER] Conversation history cleared")

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Simple chat method for DJ Brain decisions.

        Args:
            messages: List of message dicts [{"role": "user", "content": "..."}]
            temperature: LLM temperature (0.0-1.0)

        Returns: String response from LLM
        """
        if not self.api_key or self.api_key == "your-openrouter-api-key-here":
            print("[OPENROUTER] No API key, returning empty JSON")
            return "{}"

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 500
                },
                timeout=self.timeout
            )

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"⚠️ OpenRouter chat error: {e}")
            return "{}"


if __name__ == "__main__":
    print("Testing OpenRouter client...")

    client = OpenRouterClient()

    test_commands = [
        "Load a Techno track on Deck A",
        "Play Deck B",
        "What's currently playing?",
        "Start autonomous mode",
        "Vorrei qualcosa di energico sul deck di sinistra"
    ]

    for cmd in test_commands:
        print(f"\n[TEST] Input: {cmd}")
        result = client.parse_dj_command(cmd)
        print(f"[TEST] Result: {result}")
