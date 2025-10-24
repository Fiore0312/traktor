"""
Autonomous DJ System - Hybrid Intelligence
Combines Task agents (deep analysis) with real-time execution (MIDI immediato)

Architecture:
- live_performer.py: Real-time MIDI loop (<10ms latency)
- background_intelligence.py: Agent orchestrator (runs in background)
- human_interface.py: CLI for commands during performance
- state_manager.py: Shared state coordination
"""

__version__ = "1.0.0"
__author__ = "DJ Fiore + Claude Code"

from .state_manager import StateManager

__all__ = ["StateManager"]
