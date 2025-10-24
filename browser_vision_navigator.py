#!/usr/bin/env python3
"""
Browser Vision Navigator - Autonomous Folder Recognition
Uses OCR to read Traktor browser tree and navigate to specific folders.

Author: DJ Fiore AI System
Version: 1.0
Created: 2025-10-24
"""
from traktor_midi_driver import TraktorMIDIDriver
from PIL import Image
import pytesseract
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BrowserFolder:
    """Represents a folder in the browser tree."""
    name: str
    position: int  # Vertical position in pixels
    is_selected: bool
    indent_level: int  # Tree depth (0=root, 1=subfolder, etc)


class BrowserVisionNavigator:
    """
    Navigate Traktor browser using visual recognition and MIDI commands.
    """

    def __init__(self, midi_driver: TraktorMIDIDriver):
        """
        Initialize browser navigator.

        Args:
            midi_driver: TraktorMIDIDriver instance
        """
        self.midi = midi_driver

        # Browser control CC numbers
        self.CC_TREE_UP = 73
        self.CC_TREE_DOWN = 72
        self.CC_LIST_SCROLL = 74
        self.CC_EXPAND_COLLAPSE = 64

        # Navigation delays (Traktor needs time)
        self.SCROLL_DELAY = 0.5  # Delay after scroll command
        self.CAPTURE_DELAY = 0.3  # Delay before screenshot

    def capture_browser_area(self, save_path: str = "browser_screenshot.png") -> Image.Image:
        """
        Capture screenshot of Traktor browser area.

        Args:
            save_path: Path to save screenshot

        Returns:
            PIL Image of browser area
        """
        logger.info("[VISION] Capturing browser screenshot...")

        # Use PowerShell to capture Traktor window
        import subprocess

        # PowerShell script to capture active window
        ps_script = """
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing

        # Find Traktor window
        $traktor = Get-Process | Where-Object {$_.MainWindowTitle -like "*Traktor*"} | Select-Object -First 1

        if ($traktor) {
            # Bring to front
            [void][System.Windows.Forms.Application]::SetForegroundWindow($traktor.MainWindowHandle)
            Start-Sleep -Milliseconds 200

            # Capture screen
            $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)

            # Save
            $bitmap.Save("TEMP_PATH")
            $graphics.Dispose()
            $bitmap.Dispose()
        }
        """.replace("TEMP_PATH", save_path)

        try:
            subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
            time.sleep(0.5)

            img = Image.open(save_path)
            logger.info(f"[VISION] Screenshot captured: {img.size}")
            return img

        except Exception as e:
            logger.error(f"[VISION] Screenshot failed: {e}")
            raise

    def crop_browser_tree(self, screenshot: Image.Image) -> Image.Image:
        """
        Crop screenshot to browser tree area only.

        Args:
            screenshot: Full Traktor screenshot

        Returns:
            Cropped image of browser tree
        """
        # Browser tree typical location in Traktor (adjust if needed)
        # Left sidebar, top portion
        width, height = screenshot.size

        # Typical browser tree coordinates (left 20%, top 30-80%)
        left = int(width * 0.02)
        top = int(height * 0.30)
        right = int(width * 0.22)
        bottom = int(height * 0.80)

        cropped = screenshot.crop((left, top, right, bottom))
        logger.info(f"[VISION] Browser tree cropped: {cropped.size}")

        return cropped

    def extract_folder_names(self, browser_image: Image.Image) -> List[BrowserFolder]:
        """
        Extract folder names from browser tree using OCR.

        Args:
            browser_image: Cropped browser tree image

        Returns:
            List of BrowserFolder objects
        """
        logger.info("[VISION] Running OCR on browser tree...")

        # Convert to grayscale for better OCR
        gray = browser_image.convert('L')

        # OCR with Tesseract
        try:
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

            folders = []
            current_folder = None

            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                conf = int(ocr_data['conf'][i])

                # Skip low confidence or empty text
                if conf < 60 or not text:
                    continue

                x = ocr_data['left'][i]
                y = ocr_data['top'][i]

                # Estimate indent level from x position
                indent = x // 20  # Rough estimate

                # Check if selected (would need color analysis)
                is_selected = False  # TODO: Detect highlight color

                folder = BrowserFolder(
                    name=text,
                    position=y,
                    is_selected=is_selected,
                    indent_level=indent
                )

                folders.append(folder)
                logger.info(f"[VISION]   Found: '{text}' (y={y}, indent={indent}, conf={conf})")

            logger.info(f"[VISION] Extracted {len(folders)} folders")
            return folders

        except Exception as e:
            logger.error(f"[VISION] OCR failed: {e}")
            return []

    def find_folder_by_name(self, target_name: str) -> Optional[BrowserFolder]:
        """
        Find a folder in the current browser view.

        Args:
            target_name: Folder name to find

        Returns:
            BrowserFolder if found, None otherwise
        """
        logger.info(f"[VISION] Searching for folder: '{target_name}'")

        # Capture and analyze browser
        screenshot = self.capture_browser_area()
        browser_tree = self.crop_browser_tree(screenshot)
        folders = self.extract_folder_names(browser_tree)

        # Search for target
        for folder in folders:
            if target_name.lower() in folder.name.lower():
                logger.info(f"[VISION] Found folder: '{folder.name}' at position {folder.position}")
                return folder

        logger.warning(f"[VISION] Folder '{target_name}' not found in current view")
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
        logger.info(f"[NAVIGATE] Target folder: '{target_name}'")

        for attempt in range(max_attempts):
            logger.info(f"[NAVIGATE] Attempt {attempt + 1}/{max_attempts}")

            # Look for folder in current view
            folder = self.find_folder_by_name(target_name)

            if folder:
                logger.info(f"[NAVIGATE] Folder visible! Position: {folder.position}")

                if folder.is_selected:
                    logger.info(f"[NAVIGATE] Folder already selected!")
                    return True

                # Folder visible but not selected
                # Calculate how many scrolls needed (rough estimate)
                # Assume each scroll moves ~50 pixels
                scrolls_needed = folder.position // 50

                if scrolls_needed > 0:
                    logger.info(f"[NAVIGATE] Scrolling down {scrolls_needed} times")
                    for _ in range(scrolls_needed):
                        self.midi.send_cc(self.CC_TREE_DOWN, 1)
                        time.sleep(self.SCROLL_DELAY)
                elif scrolls_needed < 0:
                    logger.info(f"[NAVIGATE] Scrolling up {abs(scrolls_needed)} times")
                    for _ in range(abs(scrolls_needed)):
                        self.midi.send_cc(self.CC_TREE_UP, 1)
                        time.sleep(self.SCROLL_DELAY)

                # Verify selection
                time.sleep(self.CAPTURE_DELAY)
                folder_check = self.find_folder_by_name(target_name)

                if folder_check and folder_check.is_selected:
                    logger.info(f"[NAVIGATE] Successfully selected '{target_name}'!")
                    return True

            # Folder not visible, scroll down to search
            logger.info(f"[NAVIGATE] Folder not visible, scrolling down...")
            self.midi.send_cc(self.CC_TREE_DOWN, 1)
            time.sleep(self.SCROLL_DELAY)

        logger.error(f"[NAVIGATE] Failed to find folder '{target_name}' after {max_attempts} attempts")
        return False

    def get_current_folder(self) -> Optional[str]:
        """
        Get currently selected folder name.

        Returns:
            Folder name if detected, None otherwise
        """
        screenshot = self.capture_browser_area()
        browser_tree = self.crop_browser_tree(screenshot)
        folders = self.extract_folder_names(browser_tree)

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
        screenshot = self.capture_browser_area()
        browser_tree = self.crop_browser_tree(screenshot)
        folders = self.extract_folder_names(browser_tree)

        return [f.name for f in folders]


def main():
    """Demo browser vision navigation."""
    print("="*70)
    print("BROWSER VISION NAVIGATOR - DEMO")
    print("="*70)
    print()

    midi = TraktorMIDIDriver()
    navigator = BrowserVisionNavigator(midi)

    # Demo 1: List visible folders
    print("\n--- TEST 1: LIST VISIBLE FOLDERS ---")
    folders = navigator.list_visible_folders()
    print(f"\nVisible folders ({len(folders)}):")
    for i, folder in enumerate(folders, 1):
        print(f"  {i}. {folder}")

    # Demo 2: Find specific folder
    print("\n--- TEST 2: SEARCH FOR FOLDER ---")
    target = input("\nEnter folder name to search: ")

    if navigator.navigate_to_folder(target):
        print(f"\nSUCCESS: Navigated to '{target}'!")
    else:
        print(f"\nFAIL: Could not find '{target}'")

    midi.close()


if __name__ == "__main__":
    main()
