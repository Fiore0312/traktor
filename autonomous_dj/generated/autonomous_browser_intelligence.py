#!/usr/bin/env python3
"""
Autonomous Browser Intelligence - Vision-Guided Navigation
===========================================================

Integrates screenshot analysis with MIDI browser navigation for fully autonomous
track selection. This module bridges the gap between SEEING the browser state
and ACTING on it with MIDI commands.

Core Workflow:
1. Capture screenshot of Traktor browser
2. Analyze visible folder tree (OCR/visual analysis)
3. Calculate steps needed to reach target folder
4. Use browser_navigator to execute MIDI navigation
5. Verify navigation succeeded with new screenshot
6. Repeat for track selection within folder

Author: DJ Fiore AI System
Date: 2025-10-20
Version: 2.0 (integrates lessons from 2025-01-11 + 2025-10-20 sessions)
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from PIL import Image
import numpy as np
import pytesseract

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autonomous_dj.autonomous_vision_verifier import TraktorVisionVerifier
from autonomous_dj.generated import browser_navigator
from traktor_midi_driver import TraktorMIDIDriver

# Configure Tesseract OCR path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class BrowserFolderInfo:
    """Information about a visible folder in the browser"""
    name: str
    position: int  # Position in visible list (0 = top)
    is_selected: bool
    is_expanded: bool
    y_coordinate: int  # Pixel Y position in screenshot


@dataclass
class BrowserState:
    """Complete browser state from screenshot analysis"""
    visible_folders: List[BrowserFolderInfo]
    selected_folder: Optional[str]
    selected_track: Optional[str]
    browser_region: Tuple[int, int, int, int]  # (left, top, right, bottom)


class AutonomousBrowserIntelligence:
    """
    Vision-guided browser navigation for autonomous track selection.

    Combines:
    - TraktorVisionVerifier for screenshot capture
    - Visual analysis of browser tree (OCR/pixel detection)
    - browser_navigator for MIDI command execution
    - Knowledge persistence for learned folder positions
    """

    def __init__(self):
        """Initialize vision verifier and MIDI driver"""
        self.verifier = TraktorVisionVerifier()
        self.midi_driver = TraktorMIDIDriver()

        # Browser region coordinates (measured from 1920x1040 screenshot)
        # These are the pixel coordinates of the browser tree area
        # Calibrated: 2025-10-20 using analyze_browser_selection_color.py
        self.BROWSER_TREE_REGION = {
            'left': 10,
            'top': 423,     # Start at TITLE header
            'right': 200,
            'bottom': 795   # End at bottom of visible folders
        }

        # Selection highlight color (cyan/teal blue) - RGB range
        # Exact color: RGB(50, 158, 183) = #329eb7
        # Calibrated: 2025-10-20 from "Future bass" selection
        self.SELECTION_COLOR_MIN = np.array([40, 148, 173], dtype=np.uint8)
        self.SELECTION_COLOR_MAX = np.array([60, 168, 193], dtype=np.uint8)

        logger.info("AutonomousBrowserIntelligence initialized")

    def capture_browser_state(self) -> Optional[BrowserState]:
        """
        Capture and analyze current browser state.

        Returns:
            BrowserState object or None if capture failed
        """
        logger.info("Capturing browser state...")

        # Step 1: Capture screenshot
        img = self.verifier.capture_current_state(save=True)
        if img is None:
            logger.error("Failed to capture screenshot")
            return None

        logger.info(f"Screenshot captured: {img.size}")

        # Step 2: Extract browser tree region
        browser_region = self._extract_browser_region(img)
        if browser_region is None:
            logger.error("Failed to extract browser region")
            return None

        # Step 3: Analyze visible folders
        visible_folders = self._analyze_folder_tree(browser_region)

        # Step 4: Find selected folder
        selected_folder = None
        for folder in visible_folders:
            if folder.is_selected:
                selected_folder = folder.name
                break

        browser_state = BrowserState(
            visible_folders=visible_folders,
            selected_folder=selected_folder,
            selected_track=None,  # TODO: Implement track detection
            browser_region=(
                self.BROWSER_TREE_REGION['left'],
                self.BROWSER_TREE_REGION['top'],
                self.BROWSER_TREE_REGION['right'],
                self.BROWSER_TREE_REGION['bottom']
            )
        )

        logger.info(f"Browser state analyzed: {len(visible_folders)} folders visible")
        if selected_folder:
            logger.info(f"  Selected folder: {selected_folder}")

        return browser_state

    def _extract_browser_region(self, img: Image.Image) -> Optional[np.ndarray]:
        """Extract browser tree region from full screenshot"""
        try:
            # Crop to browser tree area
            browser_crop = img.crop((
                self.BROWSER_TREE_REGION['left'],
                self.BROWSER_TREE_REGION['top'],
                self.BROWSER_TREE_REGION['right'],
                self.BROWSER_TREE_REGION['bottom']
            ))

            # Convert to numpy array for analysis
            return np.array(browser_crop)
        except Exception as e:
            logger.error(f"Failed to extract browser region: {e}")
            return None

    def _analyze_folder_tree(self, browser_img: np.ndarray) -> List[BrowserFolderInfo]:
        """
        Analyze browser tree image to extract folder information.

        This is the CORE intelligence function that:
        1. Detects folder rows by scanning for text/icons
        2. Identifies which folder is selected (blue highlight)
        3. Extracts folder names (OCR or pattern matching)
        4. Returns structured list of visible folders

        Args:
            browser_img: Numpy array of browser tree region

        Returns:
            List of BrowserFolderInfo objects
        """
        folders = []

        # TODO: Implement sophisticated analysis:
        # 1. Detect horizontal bands of text (folder names)
        # 2. Use OCR to read folder names
        # 3. Detect blue selection highlight
        # 4. Detect folder expansion state (arrow icon)

        # Current: Scan for blue selection highlight (calibrated 2025-10-20)
        height, width = browser_img.shape[:2]
        logger.info(f"Scanning browser image: {width}x{height} pixels")

        # Folder rows are approximately 20 pixels tall
        row_height = 20

        # Aggregate consecutive rows with selection highlight into single folders
        current_folder_start = None
        current_folder_pixels = []

        for y in range(0, height, row_height):
            if y + row_height > height:
                break

            row_slice = browser_img[y:y+row_height, :, :]
            highlight_pixels = self._count_selection_pixels(row_slice)

            if highlight_pixels > 20:  # This row is part of a selection
                if current_folder_start is None:
                    # Start of new folder
                    current_folder_start = y
                    current_folder_pixels = [highlight_pixels]
                else:
                    # Continuation of current folder
                    current_folder_pixels.append(highlight_pixels)
            else:
                # No selection in this row
                if current_folder_start is not None:
                    # End of current folder - save it
                    total_pixels = sum(current_folder_pixels)
                    folder_center_y = current_folder_start + (len(current_folder_pixels) * row_height) // 2

                    # Extract folder name using OCR
                    folder_name = self._extract_folder_name_ocr(
                        browser_img,
                        current_folder_start,
                        len(current_folder_pixels) * row_height
                    )

                    folder = BrowserFolderInfo(
                        name=folder_name,
                        position=folder_center_y // row_height,
                        is_selected=True,
                        is_expanded=False,  # TODO: Detect expansion
                        y_coordinate=folder_center_y
                    )
                    folders.append(folder)
                    logger.info(f"  [DETECTED] Selected folder at Y={folder_center_y} ({total_pixels} total pixels, {len(current_folder_pixels)} rows)")

                    # Reset for next folder
                    current_folder_start = None
                    current_folder_pixels = []

        # Handle case where selection extends to end of image
        if current_folder_start is not None:
            total_pixels = sum(current_folder_pixels)
            folder_center_y = current_folder_start + (len(current_folder_pixels) * row_height) // 2

            # Extract folder name using OCR
            folder_name = self._extract_folder_name_ocr(
                browser_img,
                current_folder_start,
                len(current_folder_pixels) * row_height
            )

            folder = BrowserFolderInfo(
                name=folder_name,
                position=folder_center_y // row_height,
                is_selected=True,
                is_expanded=False,
                y_coordinate=folder_center_y
            )
            folders.append(folder)
            logger.info(f"  [DETECTED] Selected folder at Y={folder_center_y} ({total_pixels} total pixels, {len(current_folder_pixels)} rows)")

        if not folders:
            logger.warning("No selected folder detected in browser tree")
            logger.warning("This might indicate:")
            logger.warning("  - Selection color calibration is wrong")
            logger.warning("  - Browser tree coordinates are wrong")
            logger.warning("  - No folder is currently selected")

        return folders

    def _count_selection_pixels(self, img_slice: np.ndarray) -> int:
        """
        Count pixels matching selection highlight color.

        Args:
            img_slice: Small horizontal slice of browser image

        Returns:
            Number of pixels matching selection color
        """
        # Create mask for pixels in selection color range
        mask = np.all(
            (img_slice >= self.SELECTION_COLOR_MIN) &
            (img_slice <= self.SELECTION_COLOR_MAX),
            axis=2
        )

        return int(np.sum(mask))

    def _extract_folder_name_ocr(self, browser_img: np.ndarray, y_start: int, height: int) -> str:
        """
        Extract folder name from browser image using OCR.

        Args:
            browser_img: Full browser tree image
            y_start: Y coordinate where folder starts
            height: Height of folder row in pixels

        Returns:
            Folder name extracted via OCR, or fallback to position if OCR fails
        """
        try:
            # Extract folder row region
            row_slice = browser_img[y_start:y_start+height, :, :]

            # Convert to PIL Image for Tesseract
            pil_img = Image.fromarray(row_slice)

            # OCR configuration optimized for folder names
            # --psm 7: Treat image as single text line
            # --oem 3: Use default OCR engine mode
            custom_config = r'--psm 7 --oem 3'

            # Extract text
            text = pytesseract.image_to_string(pil_img, config=custom_config).strip()

            # Clean up OCR output
            text = text.replace('\n', ' ').strip()

            if text and len(text) > 0:
                logger.info(f"  [OCR] Extracted folder name: '{text}'")
                return text
            else:
                logger.warning(f"  [OCR] No text extracted from Y={y_start}, using fallback")
                return f"Folder_Y{y_start}"

        except Exception as e:
            logger.error(f"  [OCR] Failed to extract folder name: {e}")
            return f"Folder_Y{y_start}"

    def navigate_to_folder(self, target_folder: str) -> bool:
        """
        Navigate to target folder using vision-guided MIDI commands.

        Workflow:
        1. Capture current browser state
        2. Find target folder in visible list OR
        3. Calculate scroll direction and steps needed
        4. Execute MIDI navigation commands
        5. Verify navigation succeeded

        Args:
            target_folder: Name of folder to navigate to (e.g., "Dub")

        Returns:
            True if navigation succeeded
        """
        logger.info(f"Navigating to folder: {target_folder}")

        # Step 1: Capture current state
        current_state = self.capture_browser_state()
        if current_state is None:
            logger.error("Cannot navigate - failed to capture browser state")
            return False

        # Step 2: Check if already at target
        if current_state.selected_folder == target_folder:
            logger.info(f"Already at target folder: {target_folder}")
            return True

        # Step 3: Calculate navigation steps
        # TODO: Implement intelligent step calculation based on folder list
        # For now, use hardcoded navigation from autonomous_dub_track_loader.py

        logger.warning("Using hardcoded navigation (TODO: implement intelligent calculation)")

        # Hardcoded navigation to "Dub" folder (from previous working script)
        # Navigate down 4 steps, then expand
        for i in range(4):
            logger.info(f"Scroll folder tree DOWN (step {i+1}/4)")
            self.midi_driver.send_cc(cc_number=72, value=127)
            time.sleep(1.8)  # CRITICAL: 1.8s delay between commands

        # Expand folder
        logger.info("Expand folder")
        self.midi_driver.send_cc(cc_number=64, value=127)
        time.sleep(1.8)

        # Step 4: Verify navigation succeeded
        time.sleep(1.0)  # Wait for browser to update
        new_state = self.capture_browser_state()

        if new_state and new_state.selected_folder == target_folder:
            logger.info(f"Successfully navigated to: {target_folder}")
            return True
        else:
            logger.warning(f"Navigation verification failed (expected {target_folder})")
            return False

    def load_track_from_folder(self, folder_name: str, track_position: int = 1, deck: str = 'A') -> bool:
        """
        Complete autonomous workflow: navigate to folder and load specific track.

        Args:
            folder_name: Target folder name (e.g., "Dub")
            track_position: Track number within folder (1 = first track)
            deck: Target deck ('A' or 'B')

        Returns:
            True if track loaded successfully
        """
        logger.info(f"=== AUTONOMOUS TRACK LOADING ===")
        logger.info(f"Target: Folder '{folder_name}', Track #{track_position}, Deck {deck}")

        # Step 1: Navigate to folder
        if not self.navigate_to_folder(folder_name):
            logger.error(f"Failed to navigate to folder: {folder_name}")
            return False

        # Step 2: Select track within folder
        # First track is auto-selected after folder expansion, so position 1 needs no scroll
        if track_position > 1:
            steps_to_scroll = track_position - 1
            logger.info(f"Scrolling to track position {track_position}")
            for i in range(steps_to_scroll):
                self.midi_driver.send_cc(cc_number=74, value=127)  # Scroll track list
                time.sleep(1.8)

        # Step 3: Load track to deck
        logger.info(f"Loading track to Deck {deck}")
        load_cc = 43 if deck == 'A' else 44  # CC 43 = Deck A load, CC 44 = Deck B load
        self.midi_driver.send_cc(cc_number=load_cc, value=127)
        time.sleep(3.0)  # Wait for waveform analysis

        # Step 4: Verify track loaded
        logger.info("Verifying track loaded...")
        verification_img = self.verifier.capture_current_state(save=True)
        if verification_img:
            state = self.verifier.analyze_current_state(verification_img)
            deck_state = state.deck_a if deck == 'A' else state.deck_b

            if deck_state.state.value == 'loaded':
                logger.info(f"[SUCCESS] Track loaded to Deck {deck}")
                return True
            else:
                logger.error(f"[FAILED] Track not loaded to Deck {deck}")
                return False
        else:
            logger.warning("Could not verify track load (screenshot failed)")
            return False

    def close(self):
        """Clean up resources"""
        if self.midi_driver:
            self.midi_driver.close()
        logger.info("AutonomousBrowserIntelligence closed")


# ============================================================================
# MODULE TESTING
# ============================================================================

def main():
    """Test autonomous browser intelligence"""
    print("=" * 70)
    print("AUTONOMOUS BROWSER INTELLIGENCE - TEST")
    print("=" * 70)
    print()

    abi = AutonomousBrowserIntelligence()

    try:
        # Test 1: Capture and analyze current browser state
        print("[TEST 1] Capturing browser state...")
        state = abi.capture_browser_state()

        if state:
            print(f"[OK] Browser state captured")
            print(f"     Visible folders: {len(state.visible_folders)}")
            print(f"     Selected folder: {state.selected_folder}")

            for folder in state.visible_folders:
                print(f"       - {folder.name} (Y={folder.y_coordinate}, selected={folder.is_selected})")
        else:
            print("[FAILED] Could not capture browser state")
            return 1

        print()

        # Test 2: Navigate to Dub folder (hardcoded for now)
        # Uncomment when ready to test navigation:
        # print("[TEST 2] Navigating to 'Dub' folder...")
        # success = abi.navigate_to_folder("Dub")
        # print(f"[{'OK' if success else 'FAILED'}] Navigation result: {success}")

        print()
        print("[SUCCESS] Test completed")
        return 0

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        abi.close()


if __name__ == "__main__":
    sys.exit(main())
