"""
Workflow Controller - Orchestratore centrale DJ AI.
Coordina tutti i componenti e gestisce comandi utente.
"""

from typing import Dict, List, Optional
import time
from pathlib import Path

from autonomous_dj import config  # Import config flags
from autonomous_dj.generated.traktor_vision import TraktorVisionSystem
from autonomous_dj.claude_vision_client import ClaudeVisionClient
from autonomous_dj.openrouter_client import OpenRouterClient
from traktor_midi_driver import TraktorMIDIDriver
from traktor_safety_checks import TraktorSafetyChecks
from autonomous_dj.browser_navigator import BrowserNavigator
from autonomous_dj.hierarchical_navigator import HierarchicalNavigator
from camelot_matcher import find_compatible_tracks
from midi_navigator import TraktorNavigator
# from track_matcher import TrackMatcher  # TODO: implement


class DJWorkflowController:
    """
    Controller principale per workflow DJ autonomo.
    Riceve comandi da front-end ed esegue azioni complesse.
    """

    def __init__(self):
        """Inizializza tutti i componenti."""

        print("[CONTROLLER] Initializing DJ AI system...")

        # Check vision mode
        vision_enabled = config.USE_AI_FOR_VISION_ANALYSIS
        
        if vision_enabled:
            print("[CONTROLLER] Vision AI enabled - full features")
        else:
            print("[CONTROLLER] BLIND MODE enabled - no vision (FREE!)")

        # Core components
        self.vision = TraktorVisionSystem() if vision_enabled else None
        self.llm = OpenRouterClient()  # Natural language command parsing (always enabled)
        self.ai_vision = ClaudeVisionClient() if vision_enabled else None
        self.midi = TraktorMIDIDriver(dry_run=False)
        self.safety = TraktorSafetyChecks(self.midi)
        
        # Navigation (only if vision enabled)
        if vision_enabled:
            self.browser_nav = BrowserNavigator(self.vision, self.ai_vision, self.midi)
            self.hierarchical_nav = HierarchicalNavigator(self.vision, self.ai_vision, self.midi)
        else:
            self.browser_nav = None
            self.hierarchical_nav = None

        # State management
        self.current_state = {
            'browser': {},
            'deck_a': {},
            'deck_b': {},
            'mixer': {},
            'mode': 'manual',  # manual, assisted, autonomous
            'last_update': time.time()
        }

        # History
        self.action_history = []

        print("[CONTROLLER] System ready")
        if not vision_enabled:
            print("[CONTROLLER] NOTE: Running in BLIND MODE (no API costs)")
            print("[CONTROLLER] Vision-dependent features disabled")

    def handle_user_command(self, command: str) -> Dict:
        """
        Gestisce comando testuale da front-end.

        Args:
            command: Richiesta utente in linguaggio naturale

        Returns:
            {
                'success': bool,
                'response': str,
                'action_taken': str,
                'new_state': dict
            }
        """

        print(f"\n[CONTROLLER] User command: {command}")

        try:
            # Parse command using OpenRouter LLM (with fallback to rules)
            action_plan = self.llm.parse_dj_command(command)

            if not action_plan or action_plan.get('confidence', 0) < 0.3:
                return {
                    'success': False,
                    'response': "Non ho capito. Prova con: 'Carica traccia su Deck A', 'Play Deck B', 'Mostrami lo stato'",
                    'action_taken': 'none'
                }

            print(f"[CONTROLLER] Parsed action: {action_plan['action']}, confidence: {action_plan.get('confidence', 0)}")

            # Execute action plan
            result = self._execute_action_plan(action_plan)

            # Update state
            self.refresh_state()

            return {
                'success': result['success'],
                'response': result['message'],
                'action_taken': action_plan['action'],
                'new_state': self.current_state
            }

        except Exception as e:
            print(f"[CONTROLLER] Error: {e}")
            return {
                'success': False,
                'response': f"Errore: {str(e)}",
                'action_taken': 'error'
            }

    def _execute_action_plan(self, plan: Dict) -> Dict:
        """Esegue piano azione."""

        action = plan['action']

        if action == 'LOAD_TRACK':
            return self._action_load_track(plan)

        elif action == 'PLAY_DECK':
            return self._action_play_deck(plan)

        elif action == 'PAUSE_DECK':
            return self._action_pause_deck(plan)

        elif action == 'GET_STATUS':
            return self._action_get_status()

        elif action == 'START_AUTONOMOUS':
            return self._action_start_autonomous()

        elif action == 'NAVIGATE_FOLDER':
            return self._action_navigate_folder(plan)

        elif action == 'FIND_COMPATIBLE_TRACK':
            return self._action_find_compatible_track(plan)

        elif action == 'MIX_TRANSITION':
            return self._action_mix_transition(plan)

        else:
            return {'success': False, 'message': f"Azione {action} non implementata"}

    def _action_load_track(self, plan: Dict) -> Dict:
        """Carica traccia su deck."""

        deck = plan['deck']
        genre = plan.get('genre')
        folder = plan.get('folder')

        # Check if vision is enabled
        vision_enabled = config.USE_AI_FOR_VISION_ANALYSIS

        # 0. If folder specified, navigate to it first
        if folder:
            print(f"[CONTROLLER] Navigating to folder '{folder}' before loading track...")
            nav_result = self._action_navigate_folder({'folder': folder})

            if not nav_result['success']:
                return {
                    'success': False,
                    'message': f"Non riesco a navigare alla cartella '{folder}'. {nav_result['message']}"
                }

            print(f"[CONTROLLER] Successfully navigated to '{folder}'")
            time.sleep(1)  # Wait for UI to update

            # Select first track in folder by scrolling down once
            print("[CONTROLLER] Selecting first track in folder...")
            self.midi.browser_scroll_tracks(direction=1)
            time.sleep(0.5)

        # BLIND MODE: Skip vision analysis if disabled
        if not vision_enabled:
            print("[CONTROLLER] BLIND MODE: Vision disabled, assuming track is highlighted")
            
            # Safety check
            if not self.safety.pre_load_safety_check(deck):
                return {
                    'success': False,
                    'message': f"Safety check failed per Deck {deck}"
                }
            
            # Load track directly
            if deck == 'A':
                self.midi.load_track_deck_a()
            else:
                self.midi.load_track_deck_b()
            
            time.sleep(2)
            
            # Post-load safety
            self.safety.post_load_safety_setup(deck)
            
            return {
                'success': True,
                'message': f"✅ Track loaded on Deck {deck} (blind mode)\n"
                          f"⚠️  Volume set to 0 for safety.\n"
                          f"💡 TIP: Vision AI disabled. Make sure track was highlighted before loading!"
            }

        # NORMAL MODE: Use vision analysis
        # 1. Capture screenshot
        screenshot = self.vision.capture_traktor_window()

        # 2. Analyze UI
        analysis = self.ai_vision.analyze_traktor_screenshot(screenshot)

        # 3. Check if track highlighted
        if not analysis['browser']['track_highlighted']:
            # Try scrolling to select a track
            print("[CONTROLLER] No track highlighted, trying to select one...")
            self.midi.browser_scroll_tracks(direction=1)
            time.sleep(0.5)

            # Re-analyze
            screenshot = self.vision.capture_traktor_window()
            analysis = self.ai_vision.analyze_traktor_screenshot(screenshot)

            if not analysis['browser']['track_highlighted']:
                return {
                    'success': False,
                    'message': "Nessuna traccia evidenziata nel browser. Seleziona una traccia prima."
                }

        # 4. Safety check
        if not self.safety.pre_load_safety_check(deck):
            return {
                'success': False,
                'message': f"Safety check failed per Deck {deck}"
            }

        # 5. Load track
        if deck == 'A':
            self.midi.load_track_deck_a()
        else:
            self.midi.load_track_deck_b()

        time.sleep(2)  # Wait for load

        # 6. Post-load setup
        self.safety.post_load_safety_setup(deck)

        track_name = analysis['browser']['track_highlighted']

        return {
            'success': True,
            'message': f"Track '{track_name}' caricata su Deck {deck}!\nVolume impostato a 0 per sicurezza."
        }

    def _action_play_deck(self, plan: Dict) -> Dict:
        """Fa play su deck."""

        deck = plan['deck']

        if deck == 'A':
            self.midi.play_deck_a()
        else:
            self.midi.play_deck_b()

        return {
            'success': True,
            'message': f"Deck {deck} playing!"
        }

    def _action_pause_deck(self, plan: Dict) -> Dict:
        """Mette in pausa deck."""

        deck = plan['deck']

        if deck == 'A':
            self.midi.play_deck_a(False)
        else:
            self.midi.play_deck_b(False)

        return {
            'success': True,
            'message': f"Deck {deck} paused!"
        }

    def _action_mix_transition(self, plan: Dict) -> Dict:
        """
        Esegue un mix/transizione tra due deck.
        
        Workflow automatico:
        1. Verifica che entrambi i deck abbiano tracce
        2. Sync BPM tra i deck
        3. Start del deck target se non sta già suonando
        4. Fade crossfader graduale (8 secondi)
        5. Opzionale: fade out deck sorgente
        
        In BLIND MODE: assume che tutto sia OK e procede
        """
        
        print("[CONTROLLER] Starting mix transition...")
        
        # Determine which deck is playing (source) and which will take over (target)
        # In blind mode, assume A is playing and we mix to B
        source_deck = 'A'
        target_deck = 'B'
        
        try:
            # 1. Enable SYNC on target deck (to match BPM)
            print(f"[CONTROLLER] Enabling SYNC on Deck {target_deck}...")
            if target_deck == 'A':
                self.midi.sync_deck_a(True)
            else:
                self.midi.sync_deck_b(True)
            
            time.sleep(0.5)
            
            # 2. Start playing target deck if not already playing
            print(f"[CONTROLLER] Starting Deck {target_deck}...")
            if target_deck == 'A':
                self.midi.play_deck_a(True)
            else:
                self.midi.play_deck_b(True)
            
            time.sleep(1)
            
            # 3. Gradual crossfader transition (A→B or B→A)
            print("[CONTROLLER] Starting crossfader transition...")
            
            # Start position: full left (A) or right (B)
            # End position: opposite side
            
            if source_deck == 'A':
                # Transition A → B (left to right)
                start_pos = 0    # Full A
                end_pos = 127    # Full B
            else:
                # Transition B → A (right to left)
                start_pos = 127  # Full B
                end_pos = 0      # Full A
            
            # Gradual fade over 8 seconds (16 steps)
            steps = 16
            step_duration = 0.5  # seconds
            
            for i in range(steps + 1):
                progress = i / steps
                current_pos = int(start_pos + (end_pos - start_pos) * progress)
                
                # Set crossfader position
                self.midi.set_crossfader(current_pos)
                
                print(f"[CONTROLLER] Crossfader: {current_pos}/127 ({int(progress * 100)}%)")
                
                time.sleep(step_duration)
            
            # 4. Optional: pause source deck after transition
            print(f"[CONTROLLER] Transition complete! Deck {target_deck} is now playing.")
            
            # We can optionally pause the source deck after a few seconds
            time.sleep(2)
            
            print(f"[CONTROLLER] Pausing Deck {source_deck}...")
            if source_deck == 'A':
                self.midi.play_deck_a(False)
            else:
                self.midi.play_deck_b(False)
            
            return {
                'success': True,
                'message': f"🎧 Mix transition complete!\n\n"
                          f"✨ Transitioned from Deck {source_deck} to Deck {target_deck}\n"
                          f"⏱️ Duration: 8 seconds (smooth fade)\n"
                          f"🔄 Deck {target_deck} is now playing\n"
                          f"⏸️ Deck {source_deck} paused"
            }
            
        except Exception as e:
            print(f"[CONTROLLER] Mix transition error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f"Errore durante mix transition: {str(e)}"
            }

    def _action_get_status(self) -> Dict:
        """Ritorna stato corrente sistema."""

        self.refresh_state()

        state = self.current_state

        response = f"""STATO CORRENTE:

Browser: {state['browser'].get('track_highlighted', 'Nessuna traccia')}
Folder: {state['browser'].get('folder_name', 'N/A')}

Deck A: {state['deck_a'].get('status', 'unknown')}
{f"  -> {state['deck_a'].get('track_title')}" if state['deck_a'].get('track_title') else ""}
{f"  -> Playing: {state['deck_a'].get('playing')}" if 'playing' in state['deck_a'] else ""}

Deck B: {state['deck_b'].get('status', 'unknown')}
{f"  -> {state['deck_b'].get('track_title')}" if state['deck_b'].get('track_title') else ""}
{f"  -> Playing: {state['deck_b'].get('playing')}" if 'playing' in state['deck_b'] else ""}
"""

        return {
            'success': True,
            'message': response.strip()
        }

    def _action_start_autonomous(self, max_tracks: int = 10) -> Dict:
        """
        Start full autonomous DJ session.

        Uses Autonomous Orchestrator for complete automation:
        - Intelligent track selection (Brain + Camelot Wheel)
        - Automatic loading and mixing
        - Energy flow management

        Args:
            max_tracks: Maximum number of tracks to play (default: 10)

        Returns: Result dict with success/message
        """
        print("[CONTROLLER] 🎧 Starting AUTONOMOUS SESSION")

        # Import orchestrator (lazy import to avoid circular dependencies)
        from autonomous_dj.autonomous_orchestrator import AutonomousOrchestrator

        try:
            # Create orchestrator instance
            orchestrator = AutonomousOrchestrator(
                midi_driver=self.midi,
                start_genre="Techno",  # TODO: Make configurable
                energy_level="medium"
            )

            # Start autonomous session
            success = orchestrator.start_session()

            if not success:
                return {
                    'success': False,
                    'message': "❌ Failed to start autonomous session. Check logs for details."
                }

            # Update state
            self.current_state['mode'] = 'autonomous'

            # Run main loop in background (non-blocking for web UI)
            # NOTE: In production, this should run in a separate thread or process
            # For now, we'll run a limited session
            print(f"[CONTROLLER] Running autonomous loop for {max_tracks} tracks...")

            # This blocks until complete - in production, use threading
            orchestrator.main_loop(max_tracks=max_tracks, check_interval=2.0)

            # Session complete
            self.current_state['mode'] = 'manual'

            return {
                'success': True,
                'message': f"✅ Autonomous session complete!\n"
                          f"🎧 Played {orchestrator.tracks_played} tracks\n"
                          f"⏱️ Session duration: {int((time.time() - orchestrator.session_start_time) / 60)} minutes"
            }

        except Exception as e:
            print(f"[CONTROLLER] ❌ Autonomous session error: {e}")
            import traceback
            traceback.print_exc()

            self.current_state['mode'] = 'manual'

            return {
                'success': False,
                'message': f"❌ Autonomous session failed: {str(e)}"
            }

    def _action_navigate_folder(self, plan: Dict) -> Dict:
        """Naviga a una cartella nel browser usando vision-guided navigation."""

        folder_name = plan.get('folder', '')
        
        if not folder_name:
            return {
                'success': False,
                'message': "Specifica una cartella dove navigare"
            }

        # Check if vision is available
        vision_enabled = config.USE_AI_FOR_VISION_ANALYSIS
        
        if not vision_enabled or self.hierarchical_nav is None:
            # BLIND MODE: Simple MIDI navigation
            print(f"[CONTROLLER] BLIND MODE: Attempting simple navigation to '{folder_name}'...")
            
            # In blind mode, we can only do basic scrolling
            # This assumes the folder is somewhere in the list
            # Not as reliable as vision-guided, but it's free!
            
            # Try scrolling down to find it (max 20 scrolls)
            for i in range(20):
                self.midi.browser_scroll_tracks(direction=1)
                time.sleep(0.2)
            
            return {
                'success': True,
                'message': f"⚠️ Blind navigation to '{folder_name}'\n"
                          f"Scrolled down 20 times. Please verify manually.\n"
                          f"💡 For accurate navigation, enable Vision AI."
            }

        # NORMAL MODE: Use vision-guided navigation
        print(f"[CONTROLLER] Navigating to folder '{folder_name}' with vision guidance...")

        try:
            success = self.hierarchical_nav.navigate_to_nested_folder(folder_name)

            if success:
                return {
                    'success': True,
                    'message': f"Navigato alla cartella '{folder_name}' usando vision AI"
                }
            else:
                return {
                    'success': False,
                    'message': f"Non riesco a trovare la cartella '{folder_name}'. Prova a posizionarti manualmente piu vicino."
                }
        except Exception as e:
            print(f"[CONTROLLER] Navigation error: {e}")
            return {
                'success': False,
                'message': f"Errore durante navigazione: {str(e)}"
            }

    def _action_find_compatible_track(self, plan: Dict) -> Dict:
        """
        Trova e carica una traccia compatibile usando Camelot Wheel + BPM matching.
        
        Workflow:
        1. Analizza deck corrente per estrarre BPM/Key
        2. Trova tracce compatibili nel database
        3. Naviga alla traccia migliore
        4. Carica sul deck target
        """
        
        target_deck = plan.get('deck', 'B')  # Default: carica su B
        source_deck = 'A' if target_deck == 'B' else 'B'
        
        print(f"[CONTROLLER] Finding compatible track for Deck {source_deck} to load on Deck {target_deck}")
        
        # Check if vision is enabled
        vision_enabled = config.USE_AI_FOR_VISION_ANALYSIS
        
        try:
            # 1. Get current state (with or without vision)
            if vision_enabled:
                screenshot = self.vision.capture_traktor_window()
                analysis = self.ai_vision.analyze_traktor_screenshot(screenshot)
                
                # 2. Extract BPM and Key from source deck
                source_deck_state = analysis.get(f'deck_{source_deck.lower()}', {})
                
                current_bpm = source_deck_state.get('bpm')
                current_key = source_deck_state.get('key')
                
                # Fallback: use default values if not detected
                if not current_bpm:
                    print("[CONTROLLER] Warning: BPM not detected, using default 128 BPM")
                    current_bpm = 128.0
                
                if not current_key:
                    print("[CONTROLLER] Warning: Key not detected, using default 8A")
                    current_key = '8A'
            else:
                # BLIND MODE: Use default values directly
                print("[CONTROLLER] BLIND MODE: Using default 128 BPM, 8A")
                current_bpm = 128.0
                current_key = '8A'
            
            print(f"[CONTROLLER] Source: Deck {source_deck} @ {current_bpm} BPM, {current_key}")
            
            # 3. Find compatible tracks
            compatible_tracks = find_compatible_tracks(
                current_bpm=float(current_bpm),
                current_camelot=current_key,
                db_path='tracks.db'
            )
            
            if not compatible_tracks or len(compatible_tracks) == 0:
                return {
                    'success': False,
                    'message': f"Nessuna traccia compatibile trovata per {current_bpm} BPM, {current_key}. "
                              f"Assicurati che le tracce abbiano BPM e Key analizzati in Traktor."
                }
            
            # 4. Get best match
            best_track = compatible_tracks[0]
            track_filename = best_track[2]  # filename
            track_bpm = best_track[3]       # bpm
            track_key = best_track[5]       # camelot
            track_position = best_track[7]  # position in browser
            
            print(f"[CONTROLLER] Best match: {track_filename} @ {track_bpm} BPM, {track_key}")
            print(f"[CONTROLLER] Position in browser: {track_position}")
            
            # 5. Safety check before loading
            if not self.safety.pre_load_safety_check(target_deck):
                return {
                    'success': False,
                    'message': f"Safety check failed per Deck {target_deck}"
                }
            
            # 6. Navigate to track using MIDI navigator
            print(f"[CONTROLLER] Navigating to position {track_position}...")
            nav = TraktorNavigator('Traktor MIDI Bus 1')
            nav.navigate_to(track_position)
            time.sleep(1)  # Wait for navigation
            
            # 7. Load to deck
            print(f"[CONTROLLER] Loading to Deck {target_deck}...")
            nav.load_to_deck(target_deck)
            time.sleep(2)  # Wait for load
            nav.close()
            
            # 8. Post-load safety setup
            self.safety.post_load_safety_setup(target_deck)
            
            return {
                'success': True,
                'message': f"✨ Found compatible track!\n\n"
                          f"🎵 {track_filename}\n"
                          f"🎹 Key: {track_key} (compatible with {current_key})\n"
                          f"🎚️ BPM: {track_bpm} (matches {current_bpm})\n\n"
                          f"Loaded on Deck {target_deck}. Volume set to 0 for safety."
            }
            
        except Exception as e:
            print(f"[CONTROLLER] Error in find_compatible_track: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'message': f"Errore durante ricerca traccia compatibile: {str(e)}"
            }
    def refresh_state(self):
        """Aggiorna stato corrente da screenshot."""

        # Check if vision is enabled
        vision_enabled = config.USE_AI_FOR_VISION_ANALYSIS
        
        if not vision_enabled:
            # BLIND MODE: Use dummy state (no vision)
            self.current_state = {
                'browser': {
                    'track_highlighted': 'Unknown (blind mode)',
                    'folder_name': 'Unknown'
                },
                'deck_a': {
                    'status': 'unknown',
                    'track_title': 'Unknown (blind mode)',
                    'bpm': None,
                    'key': None,
                    'playing': False
                },
                'deck_b': {
                    'status': 'unknown', 
                    'track_title': 'Unknown (blind mode)',
                    'bpm': None,
                    'key': None,
                    'playing': False
                },
                'mixer': {},
                'mode': self.current_state.get('mode', 'manual'),
                'last_update': time.time()
            }
            return

        # NORMAL MODE: Use vision analysis
        try:
            screenshot = self.vision.capture_traktor_window()
            analysis = self.ai_vision.analyze_traktor_screenshot(screenshot, verbose=False)

            self.current_state = {
                'browser': analysis['browser'],
                'deck_a': analysis['deck_a'],
                'deck_b': analysis['deck_b'],
                'mixer': analysis['mixer'],
                'mode': self.current_state.get('mode', 'manual'),
                'last_update': time.time()
            }

        except Exception as e:
            print(f"[CONTROLLER] State refresh error: {e}")

    def get_current_state(self) -> Dict:
        """Ritorna stato corrente per front-end."""
        return self.current_state

    def autonomous_loop_iteration(self):
        """
        Esegue una iterazione del loop autonomo.
        Chiamato periodicamente quando mode='autonomous'.
        """

        if self.current_state['mode'] != 'autonomous':
            return

        # Refresh state
        self.refresh_state()

        # Get AI recommendation
        screenshot = self.vision.capture_traktor_window()
        analysis = self.ai_vision.analyze_traktor_screenshot(screenshot)

        action = analysis['recommended_action']

        # Execute recommended action
        # TODO: implement autonomous execution logic

        print(f"[AUTONOMOUS] Recommended: {action['action']}")
        print(f"[AUTONOMOUS] Reasoning: {action['reasoning']}")

    def cleanup(self):
        """Cleanup resources."""
        self.midi.close()
        print("[CONTROLLER] Cleanup complete")


# Test standalone
if __name__ == "__main__":
    controller = DJWorkflowController()

    # Test command
    result = controller.handle_user_command("Mostrami lo stato")
    print(f"\nResult: {result['response']}")

    controller.cleanup()
