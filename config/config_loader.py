#!/usr/bin/env python3
"""
Configuration Loader - Single Source of Truth
==============================================

This module loads and validates all system configurations.
USE THIS instead of hardcoding CC values or system settings.

Author: DJ Fiore Autonomous System
Date: 2025-10-21
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate system configuration"""

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader

        Args:
            config_dir: Path to config directory (default: project_root/config)
        """
        if config_dir is None:
            # Auto-detect config directory
            self.config_dir = Path(__file__).parent
        else:
            self.config_dir = Path(config_dir)

        self.midi_mapping: Dict[str, Any] = {}
        self.system_state: Dict[str, Any] = {}

        self._load_configurations()

    def _load_configurations(self):
        """Load all configuration files"""
        # Load MIDI mapping
        midi_path = self.config_dir / "traktor_midi_mapping.json"
        if midi_path.exists():
            with open(midi_path, 'r', encoding='utf-8') as f:
                self.midi_mapping = json.load(f)
            logger.info(f"Loaded MIDI mapping v{self.midi_mapping.get('config_version', 'unknown')}")
        else:
            logger.error(f"MIDI mapping not found: {midi_path}")
            raise FileNotFoundError(f"Critical: {midi_path} missing")

        # Load system state
        state_path = self.config_dir / "system_state.json"
        if state_path.exists():
            with open(state_path, 'r', encoding='utf-8') as f:
                self.system_state = json.load(f)
            logger.info(f"Loaded system state v{self.system_state.get('version', 'unknown')}")
        else:
            logger.warning(f"System state not found: {state_path}")

    def get_cc(self, deck: str, control: str) -> Optional[int]:
        """
        Get CC value for a deck control

        Args:
            deck: 'deck_a', 'deck_b', 'deck_c', 'deck_d', 'mixer', 'browser', 'fx_unit_1', etc.
            control: 'play_pause', 'volume', 'load_track', etc.

        Returns:
            CC number or None if not found

        Example:
            >>> config = ConfigLoader()
            >>> config.get_cc('deck_a', 'play_pause')
            47
            >>> config.get_cc('browser', 'scroll_tree_down')
            72
        """
        if deck not in self.midi_mapping:
            logger.error(f"Unknown deck: {deck}")
            return None

        cc_value = self.midi_mapping[deck].get(control)
        if cc_value is None:
            logger.warning(f"Control '{control}' not found in {deck}")

        return cc_value

    def get_browser_behavior(self, key: str) -> Any:
        """
        Get browser navigation behavior setting

        Args:
            key: 'navigation_behavior', 'navigation_delay_ms', etc.

        Returns:
            Configuration value
        """
        return self.midi_mapping.get('browser', {}).get(key)

    def get_known_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a known issue

        Args:
            issue_id: 'issue_1', 'issue_2', etc.

        Returns:
            Issue details dict or None
        """
        return self.system_state.get('known_issues', {}).get(issue_id)

    def get_midi_port(self) -> str:
        """Get configured MIDI port name"""
        return self.midi_mapping.get('midi_settings', {}).get('port_name', 'Traktor MIDI Bus 1')

    def validate_environment(self) -> Dict[str, bool]:
        """
        Validate system environment matches requirements

        Returns:
            Dict of validation results
        """
        results = {}

        # Check MIDI mapping version
        required_version = "1.0"
        current_version = self.midi_mapping.get('config_version', '0.0')
        results['midi_mapping_version'] = (current_version == required_version)

        # Check critical notes are documented
        results['browser_2x_documented'] = 'browser_navigation' in self.midi_mapping.get('critical_notes', {})
        results['asio_requirement_documented'] = 'asio_requirement' in self.midi_mapping.get('critical_notes', {})

        # Check known issues are tracked
        results['known_issues_tracked'] = len(self.system_state.get('known_issues', {})) >= 3

        return results

    def print_summary(self):
        """Print configuration summary"""
        print("=" * 70)
        print("CONFIGURATION SUMMARY")
        print("=" * 70)
        print(f"MIDI Mapping Version: {self.midi_mapping.get('config_version', 'unknown')}")
        print(f"Last Verified: {self.midi_mapping.get('last_verified', 'unknown')}")
        print(f"MIDI Port: {self.get_midi_port()}")
        print()
        print("Critical Notes:")
        for note, value in self.midi_mapping.get('critical_notes', {}).items():
            print(f"  - {note}: {value}")
        print()
        print("Known Issues:")
        for issue_id, issue in self.system_state.get('known_issues', {}).items():
            print(f"  [{issue_id}] {issue.get('title', 'Unknown')}")
            print(f"      Status: {issue.get('status', 'unknown')}")
        print()
        print("Validation:")
        for check, passed in self.validate_environment().items():
            status = "[OK]" if passed else "[FAIL]"
            print(f"  {status} {check}")
        print("=" * 70)


# Singleton instance
_config_instance: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """
    Get singleton configuration instance

    Returns:
        ConfigLoader instance

    Example:
        >>> from config.config_loader import get_config
        >>> config = get_config()
        >>> play_cc = config.get_cc('deck_a', 'play_pause')
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigLoader()
    return _config_instance


if __name__ == "__main__":
    # Test configuration loader
    logging.basicConfig(level=logging.INFO)

    config = ConfigLoader()
    config.print_summary()

    print()
    print("Testing CC lookups:")
    print(f"  Deck A Play/Pause: CC {config.get_cc('deck_a', 'play_pause')}")
    print(f"  Deck A Volume: CC {config.get_cc('deck_a', 'volume')}")
    print(f"  Browser Scroll Down: CC {config.get_cc('browser', 'scroll_tree_down')}")
    print(f"  Browser Navigation Delay: {config.get_browser_behavior('navigation_delay_ms')}ms")
