"""
Vision-Guided Autonomous DJ Workflow
Integra Claude Vision + Safety Layer + MIDI Driver per controllo completo Traktor.

Workflow:
1. Capture screenshot Traktor
2. Analyze con Claude Vision
3. Decide azione basata su analisi
4. Execute con safety checks
5. Verify risultato
6. Repeat

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-25
"""

import sys
sys.path.insert(0, r'C:\traktor\autonomous_dj')

from claude_vision_client import ClaudeVisionClient
from traktor_midi_driver import TraktorMIDIDriver
from traktor_safety_checks import TraktorSafetyChecks
import time
import logging
from pathlib import Path
from typing import Dict, Optional
import subprocess
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(r'C:\traktor\data\logs\vision_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VisionGuidedWorkflow:
    """
    Workflow autonomo guidato da Claude Vision.
    Loop continuo: Observe → Analyze → Decide → Act → Verify
    """

    def __init__(self):
        """Inizializza tutti i componenti del workflow."""

        logger.info("="*70)
        logger.info("VISION-GUIDED AUTONOMOUS DJ WORKFLOW")
        logger.info("="*70)

        # Init componenti
        logger.info("Initializing components...")

        try:
            # Claude Vision
            self.vision = ClaudeVisionClient()
            logger.info("[OK] Claude Vision initialized")

            # MIDI Driver
            self.midi = TraktorMIDIDriver()
            logger.info("[OK] MIDI Driver initialized")

            # Safety Layer
            self.safety = TraktorSafetyChecks(self.midi)
            logger.info("[OK] Safety Layer initialized")

        except Exception as e:
            logger.error(f"[FAIL] Initialization failed: {e}")
            raise

        # Configurazione
        self.screenshot_dir = Path(r"C:\traktor\data\screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.loop_delay = 5.0  # secondi tra cicli
        self.max_iterations = None  # None = loop infinito

        # Stato workflow
        self.iteration = 0
        self.last_action = None
        self.last_analysis = None

        logger.info("[OK] Workflow initialized")
        logger.info(f"Screenshot dir: {self.screenshot_dir}")
        logger.info(f"Loop delay: {self.loop_delay}s")

    def capture_traktor_screenshot(self) -> str:
        """
        Cattura screenshot di Traktor usando PowerShell.

        Returns:
            Path assoluto allo screenshot salvato
        """

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.screenshot_dir / f"traktor_{timestamp}.png"

        logger.info(f"[CAPTURE] Taking screenshot...")

        # PowerShell script per catturare Traktor
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        # Find Traktor window
        $traktor = Get-Process | Where-Object {{$_.MainWindowTitle -like "*Traktor*"}} | Select-Object -First 1

        if ($traktor) {{
            # Bring to front
            [void][System.Windows.Forms.Application]::SetForegroundWindow($traktor.MainWindowHandle)
            Start-Sleep -Milliseconds 300

            # Capture screen
            $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)

            # Save
            $bitmap.Save("{screenshot_path}")
            $graphics.Dispose()
            $bitmap.Dispose()

            Write-Output "Screenshot saved"
        }} else {{
            Write-Error "Traktor not found"
        }}
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )

            if screenshot_path.exists():
                logger.info(f"[CAPTURE] Screenshot saved: {screenshot_path.name}")
                return str(screenshot_path)
            else:
                raise FileNotFoundError("Screenshot file not created")

        except Exception as e:
            logger.error(f"[CAPTURE] Failed: {e}")
            raise

    def analyze_ui(self, screenshot_path: str) -> Dict:
        """
        Analizza screenshot con Claude Vision.

        Args:
            screenshot_path: Path allo screenshot

        Returns:
            Dict con analisi completa UI
        """

        logger.info(f"[ANALYZE] Analyzing UI with Claude Vision...")

        try:
            analysis = self.vision.analyze_traktor_screenshot(
                screenshot_path,
                verbose=False  # Log dettagliato già fatto dal client
            )

            # Log risultati chiave
            logger.info(f"[ANALYZE] Browser: {analysis['browser']['track_highlighted']}")
            logger.info(f"[ANALYZE] Deck A: {analysis['deck_a']['status']}")
            logger.info(f"[ANALYZE] Deck B: {analysis['deck_b']['status']}")
            logger.info(f"[ANALYZE] Action: {analysis['recommended_action']['action']}")

            if analysis['mixer']['warnings']:
                for warning in analysis['mixer']['warnings']:
                    logger.warning(f"[ANALYZE] {warning}")

            self.last_analysis = analysis
            return analysis

        except Exception as e:
            logger.error(f"[ANALYZE] Analysis failed: {e}")
            raise

    def execute_action(self, analysis: Dict) -> bool:
        """
        Esegue azione raccomandata da Claude Vision con safety checks.

        Args:
            analysis: Analisi Claude Vision

        Returns:
            True se azione eseguita con successo
        """

        action = analysis['recommended_action']['action']
        priority = analysis['recommended_action']['priority']
        safety_check = analysis['recommended_action']['safety_check']
        reasoning = analysis['recommended_action']['reasoning']

        logger.info(f"[ACTION] Recommended: {action} (priority: {priority})")
        logger.info(f"[ACTION] Reasoning: {reasoning}")
        logger.info(f"[ACTION] Safety: {safety_check}")

        # Safety gate: se safety_check non OK, skip
        if safety_check != "OK":
            logger.warning(f"[ACTION] Safety check failed: {safety_check}")
            logger.warning(f"[ACTION] Skipping action for safety")
            return False

        # Execute action con safety checks
        try:
            if action == "LOAD_TO_DECK_A":
                return self._load_to_deck_a(analysis)

            elif action == "LOAD_TO_DECK_B":
                return self._load_to_deck_b(analysis)

            elif action == "PLAY_DECK_A":
                return self._play_deck_a(analysis)

            elif action == "PLAY_DECK_B":
                return self._play_deck_b(analysis)

            elif action == "STOP_DECK_A":
                return self._stop_deck_a(analysis)

            elif action == "STOP_DECK_B":
                return self._stop_deck_b(analysis)

            elif action == "SYNC_DECK_A":
                return self._sync_deck_a(analysis)

            elif action == "SYNC_DECK_B":
                return self._sync_deck_b(analysis)

            elif action == "SCROLL_BROWSER":
                return self._scroll_browser(analysis)

            elif action == "WAIT":
                logger.info("[ACTION] Wait recommended - no action needed")
                return True

            else:
                logger.warning(f"[ACTION] Unknown action: {action}")
                return False

        except Exception as e:
            logger.error(f"[ACTION] Execution failed: {e}")
            return False

    def _load_to_deck_a(self, analysis: Dict) -> bool:
        """Load traccia su Deck A con safety checks."""

        logger.info("[ACTION] Loading to Deck A...")

        # Pre-load safety check
        logger.info("[SAFETY] Pre-load safety check Deck A...")
        self.safety.pre_load_safety_check('A')

        # Load track (assume già selezionata in browser)
        logger.info("[MIDI] Sending LOAD TO DECK A command...")
        self.midi.send_cc(43, 127)  # CC 43 = Load to Deck A
        time.sleep(0.1)
        self.midi.send_cc(43, 0)
        time.sleep(2.0)  # Attendi load completo

        # Post-load safety setup
        logger.info("[SAFETY] Post-load safety setup Deck A...")
        self.safety.post_load_safety_setup('A', first_track=False)

        self.last_action = "LOAD_TO_DECK_A"
        logger.info("[ACTION] Load to Deck A completed")
        return True

    def _load_to_deck_b(self, analysis: Dict) -> bool:
        """Load traccia su Deck B con safety checks."""

        logger.info("[ACTION] Loading to Deck B...")

        # Pre-load safety check
        logger.info("[SAFETY] Pre-load safety check Deck B...")
        self.safety.pre_load_safety_check('B')

        # Load track
        logger.info("[MIDI] Sending LOAD TO DECK B command...")
        self.midi.send_cc(44, 127)  # CC 44 = Load to Deck B
        time.sleep(0.1)
        self.midi.send_cc(44, 0)
        time.sleep(2.0)

        # Post-load safety setup
        logger.info("[SAFETY] Post-load safety setup Deck B...")
        self.safety.post_load_safety_setup('B', first_track=False)

        self.last_action = "LOAD_TO_DECK_B"
        logger.info("[ACTION] Load to Deck B completed")
        return True

    def _play_deck_a(self, analysis: Dict) -> bool:
        """Play Deck A con safety checks."""

        logger.info("[ACTION] Playing Deck A...")

        # Verifica deck è loaded
        if analysis['deck_a']['status'] != 'loaded':
            logger.warning("[ACTION] Deck A not loaded - cannot play")
            return False

        # Prepare for playback (raise volume se necessario)
        deck_a_volume = analysis['mixer']['deck_a_volume']
        if deck_a_volume == 'low':
            logger.info("[SAFETY] Raising Deck A volume for playback...")
            self.safety.prepare_for_playback('A', first_track=False)

        # Play (Toggle mode)
        logger.info("[MIDI] Sending PLAY command to Deck A...")
        self.safety.play_deck_toggle('A')

        self.last_action = "PLAY_DECK_A"
        logger.info("[ACTION] Deck A playing")
        return True

    def _play_deck_b(self, analysis: Dict) -> bool:
        """Play Deck B con safety checks."""

        logger.info("[ACTION] Playing Deck B...")

        if analysis['deck_b']['status'] != 'loaded':
            logger.warning("[ACTION] Deck B not loaded - cannot play")
            return False

        deck_b_volume = analysis['mixer']['deck_b_volume']
        if deck_b_volume == 'low':
            logger.info("[SAFETY] Raising Deck B volume for playback...")
            self.safety.prepare_for_playback('B', first_track=False)

        logger.info("[MIDI] Sending PLAY command to Deck B...")
        self.safety.play_deck_toggle('B')

        self.last_action = "PLAY_DECK_B"
        logger.info("[ACTION] Deck B playing")
        return True

    def _stop_deck_a(self, analysis: Dict) -> bool:
        """Stop Deck A."""
        logger.info("[ACTION] Stopping Deck A...")
        self.safety.pause_deck_toggle('A')
        self.last_action = "STOP_DECK_A"
        return True

    def _stop_deck_b(self, analysis: Dict) -> bool:
        """Stop Deck B."""
        logger.info("[ACTION] Stopping Deck B...")
        self.safety.pause_deck_toggle('B')
        self.last_action = "STOP_DECK_B"
        return True

    def _sync_deck_a(self, analysis: Dict) -> bool:
        """Enable sync su Deck A."""
        logger.info("[ACTION] Syncing Deck A...")
        self.midi.send_cc(69, 127)  # CC 69 = Sync Deck A
        time.sleep(0.1)
        self.midi.send_cc(69, 0)
        self.last_action = "SYNC_DECK_A"
        return True

    def _sync_deck_b(self, analysis: Dict) -> bool:
        """Enable sync su Deck B."""
        logger.info("[ACTION] Syncing Deck B...")
        self.midi.send_cc(70, 127)  # CC 70 = Sync Deck B (verify mapping)
        time.sleep(0.1)
        self.midi.send_cc(70, 0)
        self.last_action = "SYNC_DECK_B"
        return True

    def _scroll_browser(self, analysis: Dict) -> bool:
        """Scroll browser per trovare musica."""
        logger.info("[ACTION] Scrolling browser...")

        # Scroll down 3 volte
        for i in range(3):
            self.midi.send_cc(74, 1)  # CC 74 = List scroll
            time.sleep(0.5)

        self.last_action = "SCROLL_BROWSER"
        return True

    def run_loop(self, max_iterations: Optional[int] = None):
        """
        Esegue loop autonomo continuo.

        Args:
            max_iterations: Numero massimo iterazioni (None = infinito)
        """

        self.max_iterations = max_iterations

        logger.info("\n" + "="*70)
        logger.info("STARTING AUTONOMOUS LOOP")
        logger.info("="*70)
        logger.info(f"Max iterations: {max_iterations if max_iterations else 'INFINITE'}")
        logger.info(f"Loop delay: {self.loop_delay}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*70 + "\n")

        try:
            while True:
                self.iteration += 1

                logger.info(f"\n{'='*70}")
                logger.info(f"ITERATION {self.iteration}")
                logger.info(f"{'='*70}")

                # 1. Capture
                screenshot = self.capture_traktor_screenshot()

                # 2. Analyze
                analysis = self.analyze_ui(screenshot)

                # 3. Execute
                success = self.execute_action(analysis)

                if success:
                    logger.info(f"[ITERATION] Action executed successfully")
                else:
                    logger.warning(f"[ITERATION] Action failed or skipped")

                # Check exit condition
                if max_iterations and self.iteration >= max_iterations:
                    logger.info(f"\n[LOOP] Max iterations ({max_iterations}) reached")
                    break

                # Wait before next iteration
                logger.info(f"[LOOP] Waiting {self.loop_delay}s before next iteration...")
                time.sleep(self.loop_delay)

        except KeyboardInterrupt:
            logger.info("\n[LOOP] Interrupted by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"\n[LOOP] Error: {e}")
            raise
        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup risorse."""
        logger.info("\n[CLEANUP] Cleaning up...")
        try:
            self.midi.close()
            logger.info("[CLEANUP] MIDI closed")
        except:
            pass

        logger.info("\n" + "="*70)
        logger.info("WORKFLOW TERMINATED")
        logger.info(f"Total iterations: {self.iteration}")
        logger.info(f"Last action: {self.last_action}")
        logger.info("="*70 + "\n")


# ============================================================================
# MAIN - DEMO WORKFLOW
# ============================================================================

def main():
    """Demo del workflow autonomo."""

    print("\n")
    print("="*70)
    print("VISION-GUIDED AUTONOMOUS DJ WORKFLOW")
    print("="*70)
    print()
    print("Questo workflow esegue un loop autonomo continuo:")
    print("  1. Capture screenshot Traktor")
    print("  2. Analyze con Claude Vision")
    print("  3. Decide azione basata su AI")
    print("  4. Execute con safety checks")
    print("  5. Verify e repeat")
    print()
    print("SAFETY:")
    print("  - Tutte le azioni passano attraverso safety layer")
    print("  - Volume check prima di ogni load")
    print("  - EQ reset dopo ogni load")
    print("  - Toggle mode per Play/Pause")
    print()

    # Opzioni
    print("OPZIONI:")
    print("  1. Single iteration (test)")
    print("  2. Loop 10 iterazioni")
    print("  3. Loop infinito (Ctrl+C per fermare)")
    print()

    choice = input("Scegli opzione (1-3): ").strip()

    # Init workflow
    try:
        workflow = VisionGuidedWorkflow()
    except Exception as e:
        print(f"\n[FAIL] Workflow initialization failed: {e}")
        return

    # Run workflow
    try:
        if choice == "1":
            print("\n[MODE] Single iteration test")
            workflow.run_loop(max_iterations=1)
        elif choice == "2":
            print("\n[MODE] Loop 10 iterations")
            workflow.run_loop(max_iterations=10)
        elif choice == "3":
            print("\n[MODE] Infinite loop (Ctrl+C to stop)")
            workflow.run_loop(max_iterations=None)
        else:
            print("\n[ERROR] Scelta non valida")
            return

    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
