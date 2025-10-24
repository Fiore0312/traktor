#!/usr/bin/env python3
"""
Browser Vision Navigator - Claude Vision API
Uses Claude's vision capabilities to read Traktor browser and navigate folders.

Author: DJ Fiore AI System
Version: 2.0 (Claude Vision)
Created: 2025-10-24
"""
from traktor_midi_driver import TraktorMIDIDriver
from PIL import Image
import anthropic
import base64
import io
import time
import logging
import os
from typing import List, Dict, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BrowserFolder:
    """Represents a folder in the browser tree."""
    name: str
    is_selected: bool
    position: int  # 1-based position in visible list


class BrowserVisionNavigatorClaude:
    """
    Navigate Traktor browser using Claude Vision API for OCR.
    """

    def __init__(self, midi_driver: TraktorMIDIDriver, api_key: Optional[str] = None):
        """
        Initialize browser navigator with Claude Vision.

        Args:
            midi_driver: TraktorMIDIDriver instance
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
        """
        self.midi = midi_driver

        # Initialize Claude client
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set! Set env var or pass api_key parameter")

        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Browser control CC numbers
        self.CC_TREE_UP = 73
        self.CC_TREE_DOWN = 72
        self.CC_LIST_SCROLL = 74
        self.CC_EXPAND_COLLAPSE = 64

        # Navigation delays
        self.SCROLL_DELAY = 0.5
        self.CAPTURE_DELAY = 0.3

        logger.info("[VISION] Claude Vision Navigator initialized")

    def capture_traktor_screenshot(self, save_path: str = "traktor_screenshot.png") -> str:
        """
        Capture screenshot of Traktor window.

        Args:
            save_path: Path to save screenshot

        Returns:
            Path to saved screenshot
        """
        logger.info("[VISION] Capturing Traktor screenshot...")

        import subprocess

        # PowerShell script to capture Traktor window
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        # Find Traktor window
        $traktor = Get-Process | Where-Object {{$_.MainWindowTitle -like "*Traktor*"}} | Select-Object -First 1

        if ($traktor) {{
            # Bring to front
            [void][System.Windows.Forms.Application]::SetForegroundWindow($traktor.MainWindowHandle)
            Start-Sleep -Milliseconds 300

            # Capture full screen (Traktor window)
            $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)

            # Save
            $bitmap.Save("{save_path}")
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
                check=True
            )

            if os.path.exists(save_path):
                logger.info(f"[VISION] Screenshot saved: {save_path}")
                return save_path
            else:
                raise FileNotFoundError("Screenshot file not created")

        except Exception as e:
            logger.error(f"[VISION] Screenshot failed: {e}")
            raise

    def image_to_base64(self, image_path: str) -> str:
        """
        Convert image to base64 for Claude API.

        Args:
            image_path: Path to image file

        Returns:
            Base64 encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def analyze_browser_with_claude(self, screenshot_path: str) -> List[BrowserFolder]:
        """
        Use Claude Vision to analyze browser tree and extract folder names.

        Args:
            screenshot_path: Path to Traktor screenshot

        Returns:
            List of BrowserFolder objects
        """
        logger.info("[CLAUDE] Analyzing browser tree with Claude Vision...")

        # Convert image to base64
        image_data = self.image_to_base64(screenshot_path)

        # Prepare prompt for Claude
        prompt = """Analyze this Traktor DJ software screenshot. Focus on the BROWSER TREE on the left side.

Extract ALL visible folder names from the browser tree. For each folder:
1. The exact folder name
2. Whether it appears SELECTED/HIGHLIGHTED (different background color)
3. Its position in the visible list (1=top, 2=second, etc.)

Return ONLY a JSON array like this:
[
  {"name": "Techno", "selected": true, "position": 1},
  {"name": "House", "selected": false, "position": 2},
  {"name": "Drum & Bass", "selected": false, "position": 3}
]

IMPORTANT:
- Only include folders actually visible in the tree
- Be precise with folder names (spelling matters!)
- Identify which ONE folder is selected (highlighted)
- Position 1 = topmost visible folder

Return ONLY the JSON array, no other text."""

        try:
            # Call Claude Vision API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            # Extract response
            response_text = message.content[0].text
            logger.info(f"[CLAUDE] Response: {response_text}")

            # Parse JSON
            import json
            folders_data = json.loads(response_text)

            # Convert to BrowserFolder objects
            folders = []
            for item in folders_data:
                folder = BrowserFolder(
                    name=item['name'],
                    is_selected=item.get('selected', False),
                    position=item.get('position', 0)
                )
                folders.append(folder)
                logger.info(f"[CLAUDE]   Found: '{folder.name}' (pos={folder.position}, selected={folder.is_selected})")

            logger.info(f"[CLAUDE] Extracted {len(folders)} folders")
            return folders

        except Exception as e:
            logger.error(f"[CLAUDE] Vision analysis failed: {e}")
            return []

    def find_folder(self, target_name: str) -> Optional[BrowserFolder]:
        """
        Find a folder in current browser view.

        Args:
            target_name: Folder name to find

        Returns:
            BrowserFolder if found, None otherwise
        """
        logger.info(f"[SEARCH] Looking for folder: '{target_name}'")

        # Capture and analyze
        screenshot = self.capture_traktor_screenshot()
        time.sleep(self.CAPTURE_DELAY)
        folders = self.analyze_browser_with_claude(screenshot)

        # Search for target (case-insensitive partial match)
        for folder in folders:
            if target_name.lower() in folder.name.lower():
                logger.info(f"[SEARCH] Found: '{folder.name}' at position {folder.position}")
                return folder

        logger.warning(f"[SEARCH] Folder '{target_name}' not visible")
        return None

    def navigate_to_folder(self, target_name: str, max_attempts: int = 20) -> bool:
        """
        Navigate to a specific folder by name.

        Args:
            target_name: Folder name to navigate to
            max_attempts: Maximum scroll attempts

        Returns:
            True if folder found and selected
        """
        logger.info(f"[NAVIGATE] Target: '{target_name}'")

        for attempt in range(max_attempts):
            logger.info(f"[NAVIGATE] Attempt {attempt + 1}/{max_attempts}")

            # Look for folder
            folder = self.find_folder(target_name)

            if folder:
                if folder.is_selected:
                    logger.info(f"[NAVIGATE] Already selected: '{folder.name}'")
                    return True

                # Folder visible but not selected
                # Navigate to it by scrolling
                logger.info(f"[NAVIGATE] Folder at position {folder.position}, scrolling to select...")

                # Estimate scrolls needed (position 1 = already at top)
                if folder.position > 1:
                    scrolls = folder.position - 1
                    logger.info(f"[NAVIGATE] Scrolling down {scrolls} time(s)")

                    for _ in range(scrolls):
                        self.midi.send_cc(self.CC_TREE_DOWN, 1)
                        time.sleep(self.SCROLL_DELAY)

                # Verify selection
                time.sleep(self.CAPTURE_DELAY)
                check = self.find_folder(target_name)

                if check and check.is_selected:
                    logger.info(f"[NAVIGATE] SUCCESS: Selected '{check.name}'!")
                    return True

            # Not visible, scroll down to search more
            logger.info(f"[NAVIGATE] Not visible, scrolling down to search...")
            self.midi.send_cc(self.CC_TREE_DOWN, 1)
            time.sleep(self.SCROLL_DELAY)

        logger.error(f"[NAVIGATE] FAILED: Could not find '{target_name}' after {max_attempts} attempts")
        return False

    def get_selected_folder(self) -> Optional[str]:
        """
        Get currently selected folder name.

        Returns:
            Folder name if found, None otherwise
        """
        screenshot = self.capture_traktor_screenshot()
        time.sleep(self.CAPTURE_DELAY)
        folders = self.analyze_browser_with_claude(screenshot)

        for folder in folders:
            if folder.is_selected:
                return folder.name

        return None

    def list_visible_folders(self) -> List[str]:
        """
        List all folders visible in current browser view.

        Returns:
            List of folder names
        """
        screenshot = self.capture_traktor_screenshot()
        time.sleep(self.CAPTURE_DELAY)
        folders = self.analyze_browser_with_claude(screenshot)

        return [f.name for f in folders]


def main():
    """Demo Claude Vision browser navigation."""
    print("="*70)
    print("BROWSER VISION NAVIGATOR - Claude Vision API")
    print("="*70)
    print()
    print("This uses Claude's vision to read Traktor browser folders")
    print()

    # Check API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("ERROR: ANTHROPIC_API_KEY not set!")
        print("Set it with: set ANTHROPIC_API_KEY=your_key_here")
        return

    midi = TraktorMIDIDriver()
    navigator = BrowserVisionNavigatorClaude(midi)

    # Demo: List visible folders
    print("\n--- LISTING VISIBLE FOLDERS ---")
    print("Capturing Traktor browser...")

    folders = navigator.list_visible_folders()

    print(f"\nVisible folders ({len(folders)}):")
    for i, folder in enumerate(folders, 1):
        print(f"  {i}. {folder}")

    # Demo: Navigate to folder
    print("\n--- NAVIGATE TO FOLDER ---")
    target = input("\nEnter folder name to navigate to: ")

    if navigator.navigate_to_folder(target):
        print(f"\nSUCCESS: Navigated to '{target}'!")
        print("Traktor browser should now have that folder selected.")
    else:
        print(f"\nFAIL: Could not find '{target}'")

    midi.close()


if __name__ == "__main__":
    main()
