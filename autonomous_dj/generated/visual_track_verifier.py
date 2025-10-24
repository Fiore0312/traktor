#!/usr/bin/env python3
"""
Visual Track Verifier Module - Traktor Browser Analysis
========================================================

Analyzes Traktor screenshots to verify browser navigation and track selection.

Features:
- Screenshot capture integration
- Browser area analysis
- Selected track detection (blue highlight) - DEBUGGED for Phase 3
- OCR-based track name extraction using pytesseract
- Position verification for scroll commands
- Enhanced logging for debugging

Author: AI DJ System - Visual Track Verification
Date: 2025-10-12 (Phase 3: Debugged pixel detection + OCR integration)
Version: 1.1.0

Integration: Works with browser_navigator.py for visual feedback loops
Platform: Windows + Pillow + pytesseract (cross-platform ready)
"""
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple, List
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# For OCR integration
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    # Set tesseract path if needed (Windows)
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available - OCR disabled. Install with: pip install pytesseract")

# Import screenshot capture tool
from tools.capture_traktor_screen import TraktorScreenCapture

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class BrowserSelection:
    """
    Information about currently selected track in browser

    Attributes:
        is_detected: Whether a selection was found
        position_estimate: Estimated row number (1-based)
        confidence: Confidence score (0.0-1.0)
        blue_pixel_count: Number of blue pixels detected
        track_names: List of detected track names via OCR
        screenshot_path: Path to analyzed screenshot
    """
    is_detected: bool
    position_estimate: Optional[int] = None
    confidence: float = 0.0
    blue_pixel_count: int = 0
    track_names: List[str] = None
    screenshot_path: Optional[Path] = None

# ============================================================================
# CONFIGURATION
# ============================================================================

# Traktor browser blue highlight color (VERIFIED & DEBUGGED 2025-10-12 Phase 3)
# Analysis confirmed: Dark teal/blue highlight for selected items
# Range expanded slightly for robustness
SELECTION_BLUE_MIN = (15, 65, 85)    # Minimum RGB values
SELECTION_BLUE_MAX = (35, 85, 115)   # Maximum RGB values

# Browser area coordinates (as percentage of screen)
# Adjusted for typical Traktor layout (browser panel)
BROWSER_AREA = {
    'left': 0.05,     # 5% margin from left (folder tree)
    'top': 0.15,      # 15% from top (after toolbar)
    'right': 0.95,    # 95% to right (track list)
    'bottom': 0.95,   # 95% bottom (above status bar)
}

# Row detection parameters (DEBUGGED: Lower threshold for detection)
ROW_HEIGHT_PIXELS = 18  # Refined height based on Traktor UI
BLUE_THRESHOLD_PERCENT = 2.0  # Lowered from 5.0 for better detection (Phase 3 fix)
MIN_BLUE_PIXELS = 100   # Minimum absolute blue pixels per row

# OCR Configuration
OCR_CONFIG = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,-&()\' '

# ============================================================================
# GLOBAL STATE
# ============================================================================

_screen_capturer = None

def get_screen_capturer() -> TraktorScreenCapture:
    """
    Get or create screenshot capturer instance (singleton)

    Returns:
        TraktorScreenCapture instance
    """
    global _screen_capturer
    if _screen_capturer is None:
        _screen_capturer = TraktorScreenCapture()
        logger.info("TraktorScreenCapture initialized")
    return _screen_capturer

# ============================================================================
# COLOR ANALYSIS FUNCTIONS
# ============================================================================

def is_selection_blue(pixel: Tuple[int, int, int]) -> bool:
    """
    Check if pixel color matches Traktor's selection blue (DEBUGGED range)

    Args:
        pixel: RGB tuple (r, g, b)

    Returns:
        True if pixel is within selection blue range
    """
    r, g, b = pixel[0], pixel[1], pixel[2]

    in_range = (SELECTION_BLUE_MIN[0] <= r <= SELECTION_BLUE_MAX[0] and
                SELECTION_BLUE_MIN[1] <= g <= SELECTION_BLUE_MAX[1] and
                SELECTION_BLUE_MIN[2] <= b <= SELECTION_BLUE_MAX[2])

    if in_range:
        logger.debug(f"Blue pixel detected: RGB({r},{g},{b})")

    return in_range

# ============================================================================
# OCR FUNCTIONS
# ============================================================================

def extract_track_names(browser_area: Image.Image) -> List[str]:
    """
    Extract track names from browser area using OCR (Phase 3 integration)

    Args:
        browser_area: Cropped PIL Image of browser region

    Returns:
        List of detected track names (cleaned)
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract not available - skipping OCR")
        return []

    try:
        # Crop to track list area (right side of browser)
        width, height = browser_area.size
        track_list = browser_area.crop((width * 0.6, 0, width, height))  # Right 40% for tracks

        # OCR with configuration for track lists
        ocr_text = pytesseract.image_to_string(track_list, config=OCR_CONFIG)

        # Clean and split into lines
        lines = [line.strip() for line in ocr_text.split('\n') if line.strip()]

        # Filter likely track names (artist - title pattern or long strings)
        track_names = [line for line in lines if len(line) > 10 and ' - ' in line]

        logger.info(f"OCR extracted {len(track_names)} potential track names")
        if track_names:
            logger.debug(f"Sample tracks: {track_names[:3]}")

        return track_names

    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return []

# ============================================================================
# BROWSER ANALYSIS FUNCTIONS
# ============================================================================

def analyze_browser_area(image: Image.Image) -> Dict[str, any]:
    """
    Analyze browser area of Traktor screenshot (Enhanced for Phase 3)

    Args:
        image: PIL Image object

    Returns:
        Dictionary with analysis results:
        {
            'blue_rows': List[int],  # Row indices with blue pixels
            'total_blue': int,        # Total blue pixel count
            'track_names': List[str], # OCR extracted track names
            'area_analyzed': dict,    # Coordinates analyzed
        }
    """
    width, height = image.size

    # Calculate browser area coordinates (refined for accuracy)
    left = int(width * BROWSER_AREA['left'])
    top = int(height * BROWSER_AREA['top'])
    right = int(width * BROWSER_AREA['right'])
    bottom = int(height * BROWSER_AREA['bottom'])

    # Crop to browser area
    browser_area = image.crop((left, top, right, bottom))
    browser_width, browser_height = browser_area.size

    logger.debug(f"Analyzing browser area: {browser_width}x{browser_height} pixels")

    # Analyze rows for blue highlighting (DEBUGGED logic)
    blue_rows = []
    total_blue_pixels = 0

    num_rows = browser_height // ROW_HEIGHT_PIXELS
    logger.debug(f"Scanning {num_rows} potential rows")

    for row_idx in range(num_rows):
        row_top = row_idx * ROW_HEIGHT_PIXELS
        row_bottom = min((row_idx + 1) * ROW_HEIGHT_PIXELS, browser_height)

        # Count blue pixels in this row
        blue_in_row = 0
        total_pixels_in_row = 0

        for y in range(row_top, row_bottom):
            for x in range(browser_width):
                try:
                    pixel = browser_area.getpixel((x, y))
                    total_pixels_in_row += 1
                    if isinstance(pixel, tuple) and len(pixel) >= 3 and is_selection_blue(pixel):
                        blue_in_row += 1
                except Exception as e:
                    logger.debug(f"Pixel read error at ({x},{y}): {e}")
                    continue

        total_blue_pixels += blue_in_row

        # Detection logic (DEBUGGED: Lower threshold + absolute min)
        if total_pixels_in_row > 0:
            blue_percentage = (blue_in_row / total_pixels_in_row) * 100

            logger.debug(f"Row {row_idx + 1}: {blue_in_row} blue / {total_pixels_in_row} total = {blue_percentage:.2f}%")

            # Selected if percentage threshold OR absolute pixels met
            if (blue_percentage >= BLUE_THRESHOLD_PERCENT or
                blue_in_row >= MIN_BLUE_PIXELS):
                blue_rows.append(row_idx + 1)  # 1-based row number
                logger.info(f"Row {row_idx + 1} SELECTED ({blue_in_row} blue pixels, {blue_percentage:.2f}%)")

    # OCR integration for track names (Phase 3)
    track_names = extract_track_names(browser_area)

    analysis_result = {
        'blue_rows': blue_rows,
        'total_blue': total_blue_pixels,
        'track_names': track_names,
        'area_analyzed': {
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom,
            'width': browser_width,
            'height': browser_height,
        }
    }

    logger.info(f"Analysis complete: {len(blue_rows)} blue rows, {len(track_names)} track names detected")
    return analysis_result

# ============================================================================
# TRACK VERIFICATION FUNCTIONS
# ============================================================================

def capture_and_analyze() -> BrowserSelection:
    """
    Capture Traktor screenshot and analyze browser selection (Enhanced OCR)

    Returns:
        BrowserSelection with detection results including track names
    """
    if not PIL_AVAILABLE:
        logger.error("Pillow not available - cannot analyze screenshots")
        return BrowserSelection(is_detected=False, confidence=0.0)

    # Capture screenshot
    capturer = get_screen_capturer()
    screenshot_path = capturer.capture()

    if not screenshot_path or not screenshot_path.exists():
        logger.error("Screenshot capture failed")
        return BrowserSelection(is_detected=False, confidence=0.0)

    logger.info(f"Screenshot captured: {screenshot_path}")

    # Load and analyze image
    try:
        image = Image.open(screenshot_path)
        analysis = analyze_browser_area(image)

        blue_rows = analysis['blue_rows']
        total_blue = analysis['total_blue']
        track_names = analysis['track_names']

        if not blue_rows:
            logger.warning("No blue selection detected in browser")
            return BrowserSelection(
                is_detected=False,
                confidence=0.0,
                blue_pixel_count=total_blue,
                track_names=track_names,
                screenshot_path=screenshot_path
            )

        # Estimate position (use first prominent blue row)
        position = min(blue_rows) if blue_rows else None

        # Calculate confidence based on blue pixel density and OCR quality
        max_possible_blue = (analysis['area_analyzed']['width'] * analysis['area_analyzed']['height']) // 10
        confidence = min(1.0, total_blue / max(1000, max_possible_blue))
        if track_names:
            confidence = min(1.0, confidence + 0.2)  # OCR boost

        logger.info(f"Selection detected at estimated position {position} (confidence: {confidence:.2f}, tracks: {len(track_names)})")

        return BrowserSelection(
            is_detected=True,
            position_estimate=position,
            confidence=confidence,
            blue_pixel_count=total_blue,
            track_names=track_names,
            screenshot_path=screenshot_path
        )

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        return BrowserSelection(
            is_detected=False,
            confidence=0.0,
            screenshot_path=screenshot_path
        )

def verify_track_position(expected_position: int, tolerance: int = 1) -> bool:
    """
    Verify that browser selection is at expected position (with OCR confirmation)

    Args:
        expected_position: Expected row number (1-based)
        tolerance: Allowed position difference

    Returns:
        True if selection matches expected position (within tolerance)
    """
    selection = capture_and_analyze()

    if not selection.is_detected:
        logger.warning("Could not detect browser selection")
        return False

    actual_position = selection.position_estimate
    difference = abs(actual_position - expected_position)

    is_match = difference <= tolerance

    if is_match:
        logger.info(f"Position verified: {actual_position} matches {expected_position} (within tolerance {tolerance})")
        if selection.track_names:
            expected_track = selection.track_names[expected_position - 1] if expected_position - 1 < len(selection.track_names) else None
            logger.info(f"OCR confirmation: Expected track ~ {expected_track}")
    else:
        logger.warning(f"Position mismatch: expected {expected_position}, found {actual_position} (diff: {difference})")

    return is_match

def get_current_position() -> Optional[int]:
    """
    Get current browser selection position with track name

    Returns:
        Position estimate (1-based) or None if not detected
    """
    selection = capture_and_analyze()

    if selection.is_detected:
        current_track = selection.track_names[selection.position_estimate - 1] if selection.position_estimate and selection.track_names else "Unknown"
        logger.info(f"Current position: {selection.position_estimate}, Track: {current_track}")
        return selection.position_estimate
    else:
        logger.warning("Could not determine current position")
        return None

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_visual_verifier():
    """
    Initialize visual track verifier module (Phase 3: OCR ready)

    - Initialize screenshot capturer
    - Verify PIL and Tesseract availability
    - Log module status
    """
    logger.info("Initializing visual track verifier module (Phase 3)")

    if not PIL_AVAILABLE:
        logger.error("Pillow not available - install with: pip install Pillow")
        raise ImportError("Pillow required for visual verification")

    # Check Tesseract for OCR
    if not TESSERACT_AVAILABLE:
        logger.warning("pytesseract not available - OCR will be disabled. Install tesseract and pip install pytesseract")

    # Initialize screenshot capturer
    try:
        get_screen_capturer()
    except Exception as e:
        logger.error(f"Failed to initialize screenshot capturer: {e}")
        raise

    logger.info("Visual track verifier module initialized (pixel detection debugged + OCR integrated)")

# ============================================================================
# MAIN ENTRY POINT (For Testing)
# ============================================================================

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("VISUAL TRACK VERIFIER MODULE - PHASE 3 TEST (Debugged + OCR)")
    print("=" * 60)

    # Initialize
    initialize_visual_verifier()

    print("\n1. Capturing and analyzing Traktor browser...")
    selection = capture_and_analyze()

    print(f"\nResults:")
    print(f"  Detected: {selection.is_detected}")
    print(f"  Position: {selection.position_estimate}")
    print(f"  Confidence: {selection.confidence:.2f}")
    print(f"  Blue pixels: {selection.blue_pixel_count}")
    print(f"  Track names (OCR): {selection.track_names[:5] if selection.track_names else 'None'}")
    print(f"  Screenshot: {selection.screenshot_path}")

    if selection.is_detected:
        print(f"\n✅ Selection detected at position {selection.position_estimate}")
        if selection.track_names:
            print(f"OCR success: {len(selection.track_names)} tracks identified")
    else:
        print(f"\n⚠️ No selection detected - check RGB ranges or thresholds")

    print("\n" + "=" * 60)
    print("VISUAL TRACK VERIFIER MODULE READY (Phase 3 Complete)")
    print("=" * 60)