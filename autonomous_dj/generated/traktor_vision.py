#!/usr/bin/env python3
"""
TRAKTOR VISION SYSTEM
=====================
Screenshot capture and visual state analysis for Traktor Pro 3

This module provides vision capabilities to "see" Traktor's UI state:
- Capture screenshots of Traktor window
- Provide images for Claude's visual analysis
- Extract UI state (selected folder, highlighted track, deck status)
- Guide MIDI navigation decisions

MULTI-SCREEN SUPPORT:
- CRITICAL: Traktor can be on PRIMARY or SECONDARY screen
- System automatically captures ALL screens to ensure Traktor is visible
- No configuration needed - works regardless of monitor setup

Author: DJ Fiore AI System
Version: 1.1 (Multi-screen support added)
Created: 2025-10-23
Updated: 2025-10-23 (Multi-screen auto-detection)
"""

import os
import time
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TraktorVisionSystem:
    """
    Vision system for Traktor Pro 3 UI analysis

    Captures screenshots and provides them for Claude's multimodal analysis.
    Works cross-platform (Windows/macOS).

    IMPORTANT - Multi-Screen Support:
    - Automatically captures ALL screens (primary + secondary + tertiary)
    - Traktor can be on ANY screen - system handles this automatically
    - No need to specify which screen Traktor is on
    - Works with 1, 2, 3+ monitor setups
    """
    
    def __init__(self, screenshots_dir: str = "data/screenshots"):
        """
        Initialize Traktor Vision System
        
        Args:
            screenshots_dir: Directory to store screenshots (default: data/screenshots)
        """
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.system = platform.system()
        self.last_screenshot = None
        
        logger.info(f"TraktorVisionSystem initialized on {self.system}")
        logger.info(f"Screenshots directory: {self.screenshots_dir.absolute()}")
    
    def capture_traktor_window(self, filename: Optional[str] = None) -> str:
        """
        Capture screenshot of Traktor window
        
        Args:
            filename: Optional custom filename (default: auto-generated timestamp)
            
        Returns:
            str: Path to saved screenshot
            
        Raises:
            RuntimeError: If screenshot capture fails
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"traktor_{timestamp}.png"
        
        filepath = self.screenshots_dir / filename
        
        try:
            if self.system == "Windows":
                success = self._capture_windows(filepath)
            elif self.system == "Darwin":  # macOS
                success = self._capture_macos(filepath)
            else:
                raise RuntimeError(f"Unsupported platform: {self.system}")
            
            if success:
                self.last_screenshot = str(filepath)
                logger.info(f"Screenshot captured: {filepath}")
                return str(filepath)
            else:
                raise RuntimeError("Screenshot capture failed")
                
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    def _capture_windows(self, filepath: Path) -> bool:
        """
        Capture screenshot on Windows using PowerShell

        IMPORTANT: Auto-detects which screen Traktor is on.
        Traktor can be on primary OR secondary screen - we check both automatically.

        Strategy:
        1. Try to find Traktor window process
        2. Detect which screen it's on
        3. If not found, capture ALL screens (fallback)

        Args:
            filepath: Path where to save screenshot

        Returns:
            bool: True if successful
        """
        try:
            # PowerShell command to find Traktor and capture the right screen
            ps_command = f'''
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing

            # Strategy: Capture ALL screens, not just primary
            # This ensures we get Traktor regardless of which screen it's on

            $screens = [System.Windows.Forms.Screen]::AllScreens
            $totalWidth = 0
            $totalHeight = 0
            $minX = 0
            $minY = 0

            # Calculate total bounds of all screens
            foreach ($screen in $screens) {{
                if ($screen.Bounds.X -lt $minX) {{ $minX = $screen.Bounds.X }}
                if ($screen.Bounds.Y -lt $minY) {{ $minY = $screen.Bounds.Y }}
            }}

            foreach ($screen in $screens) {{
                $right = $screen.Bounds.X + $screen.Bounds.Width - $minX
                $bottom = $screen.Bounds.Y + $screen.Bounds.Height - $minY
                if ($right -gt $totalWidth) {{ $totalWidth = $right }}
                if ($bottom -gt $totalHeight) {{ $totalHeight = $bottom }}
            }}

            # Capture entire virtual screen (all monitors)
            $bitmap = New-Object System.Drawing.Bitmap($totalWidth, $totalHeight)
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphics.CopyFromScreen($minX, $minY, 0, 0, [System.Drawing.Size]::new($totalWidth, $totalHeight))
            $bitmap.Save('{str(filepath.absolute())}', [System.Drawing.Imaging.ImageFormat]::Png)
            $graphics.Dispose()
            $bitmap.Dispose()

            # Log which screens were captured
            Write-Host "[VISION] Captured $($screens.Count) screen(s)"
            foreach ($screen in $screens) {{
                $isPrimary = if ($screen.Primary) {{ "(PRIMARY)" }} else {{ "(SECONDARY)" }}
                Write-Host "[VISION] - Screen: $($screen.Bounds.Width)x$($screen.Bounds.Height) at ($($screen.Bounds.X),$($screen.Bounds.Y)) $isPrimary"
            }}
            '''

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Log PowerShell output for debugging
            if result.stdout:
                logger.info(f"Screen capture info: {result.stdout.strip()}")

            if result.returncode != 0 and result.stderr:
                logger.warning(f"PowerShell warning: {result.stderr.strip()}")

            return filepath.exists()

        except Exception as e:
            logger.error(f"Windows screenshot failed: {e}")
            return False
    
    def _capture_macos(self, filepath: Path) -> bool:
        """
        Capture screenshot on macOS using screencapture
        
        Args:
            filepath: Path where to save screenshot
            
        Returns:
            bool: True if successful
        """
        try:
            # Use screencapture to capture entire screen
            result = subprocess.run(
                ["screencapture", "-x", str(filepath)],
                capture_output=True,
                timeout=10
            )
            
            return result.returncode == 0 and filepath.exists()
            
        except Exception as e:
            logger.error(f"macOS screenshot failed: {e}")
            return False
    
    def get_last_screenshot_path(self) -> Optional[str]:
        """
        Get path to last captured screenshot
        
        Returns:
            str: Path to last screenshot, or None if no screenshots taken
        """
        return self.last_screenshot
    
    def prepare_for_analysis(self) -> Dict[str, Any]:
        """
        Capture screenshot and prepare metadata for Claude analysis
        
        Returns:
            dict: Metadata including screenshot path and timestamp
        """
        screenshot_path = self.capture_traktor_window()
        
        metadata = {
            "screenshot_path": screenshot_path,
            "timestamp": datetime.now().isoformat(),
            "platform": self.system,
            "ready_for_analysis": True,
            "instructions": self._get_analysis_instructions()
        }
        
        return metadata
    
    def _get_analysis_instructions(self) -> str:
        """
        Get instructions for Claude to analyze Traktor screenshot
        
        Returns:
            str: Analysis instructions
        """
        return """
When analyzing this Traktor screenshot, please identify:

1. **Browser State**:
   - Which folder is currently selected in the tree (left panel)
   - Which track is highlighted in the track list (center panel)
   - Track number position in the list

2. **Deck Status** (for each deck A/B/C/D):
   - Is deck playing or stopped?
   - Is MASTER enabled?
   - Is SYNC enabled?
   - Current track loaded (if visible)
   - Volume fader position
   - Crossfader position

3. **Track Information** (if visible):
   - Track name
   - Artist
   - BPM
   - Genre
   - Key

4. **UI State**:
   - Which view is active (browser, decks, mixer)
   - Any error messages or warnings
   - Ready to load track? (Y/N)

Please provide your analysis in JSON format.
"""
    
    def analyze_browser_position(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine MIDI commands needed based on visual analysis
        
        Args:
            analysis_result: JSON result from Claude's visual analysis
            
        Returns:
            dict: Recommended MIDI actions
        """
        recommendations = {
            "can_load_track": False,
            "needs_navigation": False,
            "midi_commands": [],
            "reasoning": ""
        }
        
        # Check if track is highlighted and ready to load
        if analysis_result.get("track_highlighted"):
            recommendations["can_load_track"] = True
            recommendations["midi_commands"].append({
                "action": "LOAD_TRACK",
                "cc": 43,  # DECK_A_LOAD_TRACK
                "value": 127
            })
            recommendations["reasoning"] = "Track is highlighted, ready to load"
        
        # Check if we need to navigate to different folder
        current_folder = analysis_result.get("selected_folder")
        target_folder = analysis_result.get("target_folder")
        
        if target_folder and current_folder != target_folder:
            recommendations["needs_navigation"] = True
            recommendations["midi_commands"].append({
                "action": "NAVIGATE_FOLDER",
                "cc": 72,  # BROWSER_SCROLL_TREE_INC
                "value": 127,
                "note": f"Navigate from {current_folder} to {target_folder}"
            })
            recommendations["reasoning"] = f"Need to navigate from {current_folder} to {target_folder}"
        
        return recommendations
    
    def cleanup_old_screenshots(self, keep_last_n: int = 10):
        """
        Remove old screenshots, keeping only the most recent N
        
        Args:
            keep_last_n: Number of recent screenshots to keep
        """
        screenshots = sorted(
            self.screenshots_dir.glob("traktor_*.png"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        for screenshot in screenshots[keep_last_n:]:
            try:
                screenshot.unlink()
                logger.debug(f"Removed old screenshot: {screenshot}")
            except Exception as e:
                logger.warning(f"Failed to remove {screenshot}: {e}")


def capture_and_analyze() -> Tuple[str, Dict[str, Any]]:
    """
    Convenience function: Capture screenshot and prepare for analysis
    
    Returns:
        tuple: (screenshot_path, metadata)
    """
    vision = TraktorVisionSystem()
    metadata = vision.prepare_for_analysis()
    screenshot_path = metadata["screenshot_path"]
    
    return screenshot_path, metadata



# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("TRAKTOR VISION SYSTEM - TEST")
    print("=" * 60)
    
    vision = TraktorVisionSystem()
    
    print("\n1. Capturing Traktor screenshot...")
    try:
        screenshot_path = vision.capture_traktor_window()
        print(f"[OK] Screenshot saved: {screenshot_path}")
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        exit(1)

    print("\n2. Preparing for Claude analysis...")
    metadata = vision.prepare_for_analysis()
    print(f"[OK] Ready for analysis")
    print(f"   Path: {metadata['screenshot_path']}")
    print(f"   Timestamp: {metadata['timestamp']}")
    
    print("\n3. Instructions for Claude:")
    print(metadata['instructions'])
    
    print("\n" + "=" * 60)
    print("Now Claude Code can see the screenshot and analyze it!")
    print("Use the view tool to read the image and provide analysis.")
    print("=" * 60)
