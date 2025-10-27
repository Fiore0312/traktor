#!/usr/bin/env python3
"""
Deck Operations Module - Production-Ready Deck Control for Traktor Pro 3

This module provides core deck control functions following professional DJ workflow rules.
Implements MASTER/SYNC logic, anti-blinking LED technology, robust MIDI communication,
and persistent learning capabilities for autonomous DJ improvement.

Author: deck-control-agent (AI DJ System)
Date: 2025-10-09
Version: 2.0.0 (Enhanced with Persistent Learning)

Critical Dependencies:
- DJ_WORKFLOW_RULES.md: Professional DJ workflow validation (33 years experience)
- send_single_cc.py: MIDI communication via subprocess
- Anti-blinking LED: 50ms debounce logic for state tracking
- llm_integration.py: Persistent learning and knowledge base system
- persistent_memory.py: Knowledge storage and retrieval for deck operations
"""

import sys
import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Add parent directory to path to import traktor_midi_driver and persistent learning
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from traktor_midi_driver import TraktorMIDIDriver

# Import persistent learning system
try:
    from .llm_integration import get_llm_decision, add_knowledge, query_knowledge_base, save_current_session
    from .persistent_memory import get_memory_system
    from langchain_core.messages import AIMessage
    PERSISTENT_LEARNING_ENABLED = True
except ImportError as e:
    # Persistent learning is optional - system works without it
    # Uncomment below for debugging if needed:
    # import logging
    # logging.debug(f"Persistent learning not available: {e}")
    PERSISTENT_LEARNING_ENABLED = False
    AIMessage = None  # Fallback


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA STRUCTURES
# ============================================================================

class DeckID(Enum):
    """Deck identifiers"""
    A = "deck_a"
    B = "deck_b"
    C = "deck_c"
    D = "deck_d"


@dataclass
class DeckState:
    """
    Current state of a deck

    Attributes:
        deck_id: Deck identifier (A, B, C, D)
        is_playing: Whether deck is currently playing
        is_master: Whether deck is MASTER tempo reference
        is_sync: Whether deck has SYNC enabled
        volume: Deck volume fader (0.0-1.0)
        bpm: Current BPM (None if no track loaded)
        key: Harmonic key (None if no track loaded)
        track_path: Path to loaded track (None if empty)
        last_play_command: Timestamp of last play command (anti-blinking)
        operation_history: List of past operations with outcomes
        performance_metrics: Track-specific performance data
    """
    deck_id: str
    is_playing: bool = False
    is_master: bool = False
    is_sync: bool = False
    volume: float = 0.85  # Default 85%
    bpm: Optional[float] = None
    key: Optional[str] = None
    track_path: Optional[str] = None
    last_play_command: Optional[float] = None
    operation_history: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeckOperationResult:
    """
    Result of a deck operation with learning feedback

    Attributes:
        operation_type: Type of operation (play, stop, load)
        deck_id: Deck identifier
        success: Whether operation succeeded
        track_path: Track involved (if applicable)
        reasoning: LLM reasoning or rule-based logic used
        timestamp: Operation timestamp
        feedback_score: Success feedback score (0.0-1.0)
        metadata: Additional context for learning
    """
    operation_type: str
    deck_id: str
    success: bool
    track_path: Optional[str] = None
    reasoning: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    feedback_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# MIDI CC MAPPING (Traktor Pro 3)
# ============================================================================

# Deck A MIDI CC Controls
# Remove local CCs - use TraktorCC from driver
from traktor_midi_driver import TraktorCC  # Definitive mappings

# CC Mapping Dictionary - now uses TraktorCC enum
DECK_CC_MAP = {
    'A': {
        'play': TraktorCC.DECK_A_PLAY_PAUSE,
        'cue': TraktorCC.DECK_A_CUE,
        'sync': TraktorCC.DECK_A_SYNC_GRID,
        'master': TraktorCC.DECK_A_TEMPO_MASTER,
        'volume': TraktorCC.DECK_A_VOLUME,
    },
    'B': {
        'play': TraktorCC.DECK_B_PLAY_PAUSE,
        'cue': TraktorCC.DECK_B_CUE,
        'sync': TraktorCC.DECK_B_SYNC_GRID,
        'master': TraktorCC.DECK_B_TEMPO_MASTER,
        'volume': TraktorCC.DECK_B_VOLUME,
    },
    'C': {
        'play': TraktorCC.DECK_C_PLAY_PAUSE,
        'cue': TraktorCC.DECK_C_CUE,
        'sync': TraktorCC.DECK_C_SYNC_ON,  # Or DECK_C_SYNC_GRID if preferred
        'master': TraktorCC.DECK_C_TEMPO_MASTER,
        'volume': TraktorCC.DECK_C_VOLUME,
    },
    'D': {
        'play': TraktorCC.DECK_D_PLAY_PAUSE,
        'cue': TraktorCC.DECK_D_CUE,
        'sync': TraktorCC.DECK_D_SYNC_ON,
        'master': TraktorCC.DECK_D_TEMPO_MASTER,
        'volume': TraktorCC.DECK_D_VOLUME,
    }
}


# ============================================================================
# GLOBAL STATE TRACKING (Anti-Blinking LED Technology)
# ============================================================================

# In-memory deck states for all four decks
_deck_states: Dict[str, DeckState] = {
    'A': DeckState(deck_id='A'),
    'B': DeckState(deck_id='B'),
    'C': DeckState(deck_id='C'),
    'D': DeckState(deck_id='D'),
}

# Anti-blinking debounce threshold (milliseconds)
DEBOUNCE_MS = 50

# MIDI driver instance (module-level singleton)
_midi_driver = None


def get_midi_driver() -> TraktorMIDIDriver:
    """
    Get or create MIDI driver instance (singleton pattern)

    Returns:
        TraktorMIDIDriver instance
    """
    global _midi_driver
    if _midi_driver is None:
        _midi_driver = TraktorMIDIDriver()
        logger.info("TraktorMIDIDriver initialized successfully")
    return _midi_driver


# ============================================================================
# MIDI COMMUNICATION FUNCTIONS
# ============================================================================

def send_midi_cc(cc_number: int, value: int) -> bool:
    """
    Send MIDI CC command to Traktor via TraktorMIDIDriver

    Args:
        cc_number: MIDI CC number (0-127)
        value: MIDI value (0-127)

    Returns:
        True if MIDI command sent successfully

    Raises:
        RuntimeError: If MIDI communication fails
    """
    try:
        driver = get_midi_driver()
        success = driver.send_cc(cc_number, value)

        if not success:
            logger.error(
                f"MIDI command failed: CC {cc_number} = {value}",
                extra={'cc_number': cc_number, 'value': value}
            )
            raise RuntimeError(f"MIDI command failed: CC {cc_number} = {value}")

        logger.debug(
            f"MIDI sent: CC {cc_number} = {value}",
            extra={'cc_number': cc_number, 'value': value}
        )
        return True

    except Exception as e:
        logger.error(
            f"MIDI communication error: {str(e)}",
            extra={'cc_number': cc_number, 'error': str(e)}
        )
        raise


def set_deck_master(deck_id: str, enable: bool) -> bool:
    """
    Set deck MASTER status

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        enable: True to enable MASTER, False to disable

    Returns:
        True on success
    """
    cc_number = DECK_CC_MAP[deck_id]['master']
    value = 127 if enable else 0

    success = send_midi_cc(cc_number, value)

    if success:
        _deck_states[deck_id].is_master = enable
        logger.info(
            f"Deck {deck_id} MASTER {'enabled' if enable else 'disabled'}",
            extra={'deck': deck_id, 'master': enable}
        )

    return success


def set_deck_sync(deck_id: str, enable: bool) -> bool:
    """
    Set deck SYNC status

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        enable: True to enable SYNC, False to disable

    Returns:
        True on success
    """
    cc_number = DECK_CC_MAP[deck_id]['sync']
    value = 127 if enable else 0

    success = send_midi_cc(cc_number, value)

    if success:
        _deck_states[deck_id].is_sync = enable
        logger.info(
            f"Deck {deck_id} SYNC {'enabled' if enable else 'disabled'}",
            extra={'deck': deck_id, 'sync': enable}
        )

    return success


def set_deck_volume(deck_id: str, volume: float) -> bool:
    """
    Set deck volume fader

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        volume: Volume level (0.0-1.0)

    Returns:
        True on success
    """
    # Validate volume range
    volume = max(0.0, min(1.0, volume))

    # Convert to MIDI value (0-127)
    midi_value = int(volume * 127)

    cc_number = DECK_CC_MAP[deck_id]['volume']
    success = send_midi_cc(cc_number, midi_value)

    if success:
        _deck_states[deck_id].volume = volume
        logger.info(
            f"Deck {deck_id} volume set to {volume:.2f}",
            extra={'deck': deck_id, 'volume': volume, 'midi_value': midi_value}
        )

    return success


# ============================================================================
# DECK STATE QUERY FUNCTIONS
# ============================================================================

def get_deck_state(deck_id: str) -> Dict[str, Any]:
    """
    Get current deck state

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')

    Returns:
        Dictionary containing deck state:
        {
            'deck_id': str,
            'is_playing': bool,
            'is_master': bool,
            'is_sync': bool,
            'volume': float,
            'bpm': Optional[float],
            'key': Optional[str],
            'track_path': Optional[str]
        }

    Example:
        >>> state = get_deck_state('A')
        >>> print(f"Deck A playing: {state['is_playing']}")
    """
    state = _deck_states[deck_id]
    return {
        'deck_id': state.deck_id,
        'is_playing': state.is_playing,
        'is_master': state.is_master,
        'is_sync': state.is_sync,
        'volume': state.volume,
        'bpm': state.bpm,
        'key': state.key,
        'track_path': state.track_path,
    }


def check_any_deck_playing() -> bool:
    """
    Check if ANY deck is currently playing

    This is critical for MASTER/SYNC logic per DJ_WORKFLOW_RULES.md

    Returns:
        True if at least one deck is playing

    Example:
        >>> if not check_any_deck_playing():
        ...     # First track - set as MASTER
        ...     set_deck_master('A', True)
    """
    return any(state.is_playing for state in _deck_states.values())


def get_master_deck() -> Optional[str]:
    """
    Get which deck is currently MASTER

    Returns:
        Deck ID ('A', 'B', 'C', 'D') or None if no MASTER set
    """
    for deck_id, state in _deck_states.items():
        if state.is_master:
            return deck_id
    return None


# ============================================================================
# KNOWLEDGE BASE QUERY FUNCTIONS
# ============================================================================

def query_playback_optimal_decision(deck_id: str, track_path: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query knowledge base for optimal playback decisions in similar situations

    Args:
        deck_id: Target deck identifier
        track_path: Path to track being considered
        current_state: Current DJ system state

    Returns:
        Dictionary with optimal timing, volume, and MASTER/SYNC decisions
    """
    if not PERSISTENT_LEARNING_ENABLED:
        return {'reasoning': 'Persistent learning disabled', 'confidence': 0.0}

    try:
        # Extract track metadata for context
        track_name = Path(track_path).name

        query = f"Optimal playback decision for deck {deck_id} with track {track_name}"

        # Search knowledge base for similar playback decisions
        knowledge_results = query_knowledge_base(
            query,
            decision_type='playback_timing',
            limit=5
        )

        if knowledge_results:
            # Analyze past successful decisions
            successful_decisions = [
                doc for doc in knowledge_results
                if doc.metadata.get('success_score', 0) > 0.7
            ]

            if successful_decisions:
                # Extract common patterns from successful decisions
                patterns = {
                    'optimal_volume': 0.85,  # Default
                    'should_be_master': True,  # Default
                    'should_enable_sync': False,  # Default
                    'timing_delay': 0.0,
                    'confidence': 0.0
                }

                volume_values = []
                master_decisions = []
                sync_decisions = []

                for doc in successful_decisions:
                    metadata = doc.metadata
                    if 'volume' in metadata:
                        volume_values.append(metadata['volume'])
                    if 'is_master' in metadata:
                        master_decisions.append(metadata['is_master'])
                    if 'is_sync' in metadata:
                        sync_decisions.append(metadata['is_sync'])

                # Calculate pattern averages
                if volume_values:
                    patterns['optimal_volume'] = sum(volume_values) / len(volume_values)
                if master_decisions:
                    patterns['should_be_master'] = sum(master_decisions) / len(master_decisions) > 0.5
                if sync_decisions:
                    patterns['should_enable_sync'] = sum(sync_decisions) / len(sync_decisions) > 0.5

                patterns['confidence'] = len(successful_decisions) / 5.0  # Max confidence based on results
                patterns['reasoning'] = f"Based on {len(successful_decisions)} similar successful decisions"

                return patterns

    except Exception as e:
        logger.error(f"Error querying playback knowledge: {e}")

    return {'reasoning': 'No relevant knowledge found', 'confidence': 0.0}


def query_stop_timing_analysis(deck_id: str, track_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query knowledge base for optimal stop timing decisions

    Args:
        deck_id: Deck identifier
        track_info: Current track information (BPM, remaining time, etc.)

    Returns:
        Dictionary with optimal stop timing and crowd energy considerations
    """
    if not PERSISTENT_LEARNING_ENABLED:
        return {'should_stop': True, 'reasoning': 'No learning data available', 'confidence': 0.0}

    try:
        query = f"Optimal stop timing for deck {deck_id} track BPM {track_info.get('bpm', 'unknown')}"

        knowledge_results = query_knowledge_base(
            query,
            decision_type='stop_timing',
            limit=3
        )

        if knowledge_results:
            # Analyze past stop decisions
            successful_stops = [
                doc for doc in knowledge_results
                if doc.metadata.get('success_score', 0) > 0.6
            ]

            if successful_stops:
                return {
                    'should_stop': True,
                    'optimal_remaining_time': 30,  # Default 30 seconds
                    'reasoning': f"Based on {len(successful_stops)} successful stop patterns",
                    'confidence': len(successful_stops) / 3.0
                }

    except Exception as e:
        logger.error(f"Error querying stop timing knowledge: {e}")

    return {'should_stop': True, 'reasoning': 'Default: stop when track ends', 'confidence': 0.0}


def query_track_loading_decision(deck_id: str, track_path: str, transition_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Query knowledge base for track loading compatibility and timing

    Args:
        deck_id: Target deck identifier
        track_path: Path to track to load
        transition_context: Current transition situation (genre, energy, BPM)

    Returns:
        Dictionary with loading compatibility and optimal timing
    """
    if not PERSISTENT_LEARNING_ENABLED:
        return {'should_load': True, 'compatibility': 1.0, 'reasoning': 'No learning data available'}

    try:
        track_name = Path(track_path).name
        current_genre = transition_context.get('genre', 'unknown')
        current_energy = transition_context.get('energy_level', 'unknown')

        query = f"Load track {track_name} for {current_genre} {current_energy} transition"

        knowledge_results = query_knowledge_base(
            query,
            decision_type='track_selection',
            limit=5
        )

        if knowledge_results:
            # Analyze loading compatibility
            successful_loads = [
                doc for doc in knowledge_results
                if doc.metadata.get('success_score', 0) > 0.7
            ]

            if successful_loads:
                return {
                    'should_load': True,
                    'compatibility': sum(doc.metadata.get('success_score', 0) for doc in successful_loads) / len(successful_loads),
                    'reasoning': f"Track compatible based on {len(successful_loads)} successful selections",
                    'confidence': len(successful_loads) / 5.0
                }

    except Exception as e:
        logger.error(f"Error querying track loading knowledge: {e}")

    return {'should_load': True, 'compatibility': 0.5, 'reasoning': 'No preference data available'}


def log_deck_operation(result: DeckOperationResult) -> None:
    """
    Log deck operation to persistent learning system

    Args:
        result: Operation result to log
    """
    if not PERSISTENT_LEARNING_ENABLED:
        logger.debug(f"Learning disabled: Skipping log of {result.operation_type} on deck {result.deck_id}")
        return

    try:
        # Create metadata for knowledge entry
        metadata = {
            'deck_id': result.deck_id,
            'operation_type': result.operation_type,
            'success': result.success,
            'feedback_score': result.feedback_score,
            'track_name': Path(result.track_path).name if result.track_path else 'unknown',
            'reasoning': result.reasoning
        }

        # Add result-specific metadata
        metadata.update(result.metadata)

        # Create content description
        if result.operation_type == 'play':
            content = f"Played track {Path(result.track_path).name if result.track_path else 'unknown'} on deck {result.deck_id}. {result.reasoning}"
        elif result.operation_type == 'stop':
            content = f"Stopped deck {result.deck_id}. {result.reasoning}"
        elif result.operation_type == 'load':
            content = f"Loaded track {Path(result.track_path).name if result.track_path else 'unknown'} on deck {result.deck_id}. {result.reasoning}"
        else:
            content = f"Performed {result.operation_type} on deck {result.deck_id}. {result.reasoning}"

        # Add to knowledge base
        add_knowledge(
            decision_type=f"deck_{result.operation_type}",
            content=content,
            metadata=metadata,
            success_score=result.feedback_score
        )

        logger.info(
            f"Logged operation to knowledge base: {result.operation_type} on deck {result.deck_id} (score: {result.feedback_score:.2f})",
            extra={'operation': result.operation_type, 'deck': result.deck_id, 'score': result.feedback_score}
        )

        # Save session
        save_current_session()

    except Exception as e:
        logger.error(f"Failed to log deck operation: {e}")


def provide_master_coordinator_feedback(result: DeckOperationResult, system_state: Dict[str, Any]) -> None:
    """
    Provide feedback to master coordinator about operation success/failure

    Args:
        result: Operation result to report
        system_state: Current DJ system state for context
    """
    if not PERSISTENT_LEARNING_ENABLED:
        return

    try:
        # Create feedback message for master coordinator
        feedback = {
            'source': 'deck_operations',
            'operation': result.operation_type,
            'deck': result.deck_id,
            'success': result.success,
            'feedback_score': result.feedback_score,
            'timestamp': result.timestamp,
            'reasoning': result.reasoning,
            'system_state': system_state
        }

        # Add operation-specific feedback
        if result.operation_type == 'play':
            feedback['event_type'] = 'track_started'
            feedback['track'] = Path(result.track_path).name if result.track_path else 'unknown'
        elif result.operation_type == 'stop':
            feedback['event_type'] = 'track_stopped'
        elif result.operation_type == 'load':
            feedback['event_type'] = 'track_loaded'
            feedback['track'] = Path(result.track_path).name if result.track_path else 'unknown'

        # Log feedback to conversation memory for master coordinator awareness
        memory_system = get_memory_system()
        feedback_msg = f"Deck operation feedback: {json.dumps(feedback, indent=2)}"

        # Add to conversation memory as AI message (self-generated insight)
        if AIMessage:
            memory_system.conversation_history.append(
                AIMessage(content=f"[DECK_OPERATIONS_FEEDBACK] {feedback_msg}")
            )

    except Exception as e:
        logger.error(f"Failed to provide master coordinator feedback: {e}")


# ============================================================================
# CORE DECK CONTROL FUNCTIONS (Enhanced with Persistent Learning)
# ============================================================================

def load_track(deck_id: str, track_path: str, transition_context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Load track onto specified deck with persistent learning integration

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        track_path: Absolute path to audio file
        transition_context: Current transition situation (genre, energy, BPM) for learning

    Returns:
        True on success

    Raises:
        FileNotFoundError: If track_path does not exist
        RuntimeError: If MIDI communication fails

    Example:
        >>> success = load_track('A', '/path/to/track.mp3', {'genre': 'techno', 'energy': 'high'})
        >>> if success:
        ...     print("Track loaded successfully")
    """
    if transition_context is None:
        transition_context = {}

    result = DeckOperationResult(
        operation_type='load',
        deck_id=deck_id,
        success=False,
        track_path=track_path,
        reasoning=""
    )

    try:
        # Query knowledge base for track loading decision
        load_decision = query_track_loading_decision(deck_id, track_path, transition_context)
        result.metadata['load_compatibility'] = load_decision.get('compatibility', 0.5)
        result.metadata['load_confidence'] = load_decision.get('confidence', 0.0)

        if not load_decision.get('should_load', True):
            result.reasoning = f"Track not recommended: {load_decision.get('reasoning', 'Unknown reason')}"
            logger.warning(f"Track loading not recommended: {result.reasoning}")
            # Still load (user override), but with low feedback score
            result.feedback_score = 0.3
        else:
            result.reasoning = load_decision.get('reasoning', 'Valid track for loading')
            result.feedback_score = 0.8 if load_decision.get('confidence', 0) > 0.5 else 0.6

        # Validate track exists
        track_file = Path(track_path)
        if not track_file.exists():
            result.reasoning = f"Track file not found: {track_path}"
            result.feedback_score = 0.0
            logger.error(
                f"Track file not found: {track_path}",
                extra={'deck': deck_id, 'track_path': track_path}
            )
            log_deck_operation(result)
            provide_master_coordinator_feedback(result, get_all_deck_states())
            raise FileNotFoundError(f"Track not found: {track_path}")

        # Update state
        _deck_states[deck_id].track_path = track_path
        _deck_states[deck_id].performance_metrics['last_loaded'] = datetime.now().isoformat()
        _deck_states[deck_id].performance_metrics['load_compatibility'] = load_decision.get('compatibility', 0.5)

        result.success = True
        result.metadata['track_name'] = track_file.name
        result.metadata['file_size'] = track_file.stat().st_size if track_file.exists() else 0

        logger.info(
            f"Track loaded on Deck {deck_id}: {track_file.name} (compatibility: {load_decision.get('compatibility', 0.5):.2f})",
            extra={
                'deck': deck_id,
                'track_path': track_path,
                'compatibility': load_decision.get('compatibility', 0.5),
                'confidence': load_decision.get('confidence', 0.0)
            }
        )

        # NOTE: Actual track loading in Traktor requires browser navigation
        # This function updates state and validates the file
        # Actual MIDI load commands would be sent by library-management-agent

        # Log successful operation to learning system
        log_deck_operation(result)
        provide_master_coordinator_feedback(result, get_all_deck_states())

        return True

    except Exception as e:
        result.success = False
        result.reasoning = f"Failed to load track: {str(e)}"
        result.feedback_score = 0.0

        logger.error(
            f"Failed to load track on Deck {deck_id}: {str(e)}",
            extra={'deck': deck_id, 'track_path': track_path, 'error': str(e)}
        )

        # Log failed operation to learning system
        log_deck_operation(result)
        provide_master_coordinator_feedback(result, get_all_deck_states())

        raise


def stop_deck(deck_id: str, crowd_energy_context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Stop playback on specified deck with crowd energy learning and timing optimization

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        crowd_energy_context: Current crowd energy and timing context for learning

    Returns:
        True on success

    Example:
        >>> stop_deck('A', {'energy': 'high', 'optimal_stop_time': 30})
    """
    if crowd_energy_context is None:
        crowd_energy_context = {}

    state = _deck_states[deck_id]

    result = DeckOperationResult(
        operation_type='stop',
        deck_id=deck_id,
        success=False,
        track_path=state.track_path,
        reasoning=""
    )

    try:
        # If not playing, nothing to do but log for learning
        if not state.is_playing:
            result.reasoning = "Deck already stopped"
            result.feedback_score = 1.0  # Correctly identified state

            logger.debug(
                f"Deck {deck_id} already stopped",
                extra={'deck': deck_id}
            )

            # Log state awareness to learning system
            log_deck_operation(result)
            return True

        # Query knowledge base for optimal stop timing
        track_info = {
            'bpm': state.bpm,
            'track_name': Path(state.track_path).name if state.track_path else 'unknown',
            'playback_duration': state.performance_metrics.get('playback_duration', 0)
        }

        timing_analysis = query_stop_timing_analysis(deck_id, track_info)
        result.metadata['optimal_remaining_time'] = timing_analysis.get('optimal_remaining_time', 30)
        result.metadata['stop_confidence'] = timing_analysis.get('confidence', 0.0)

        # Determine if this is good timing to stop
        should_stop_timing = timing_analysis.get('should_stop', True)
        if not should_stop_timing and crowd_energy_context.get('force_stop', False):
            result.reasoning = f"Forced stop (not optimal: {timing_analysis.get('reasoning', 'Unknown')})"
            result.feedback_score = 0.6  # Reduced score for suboptimal timing
        elif should_stop_timing:
            result.reasoning = timing_analysis.get('reasoning', 'Optimal stop timing')
            result.feedback_score = 0.8 if timing_analysis.get('confidence', 0) > 0.5 else 0.6
        else:
            result.reasoning = f"Continue playback: {timing_analysis.get('reasoning', 'Not optimal timing')}"
            result.feedback_score = 0.4

        # Send play/pause toggle (same CC stops playback)
        cc_number = DECK_CC_MAP[deck_id]['play']
        success = send_midi_cc(cc_number, 127)

        if success:
            # Update state with timing information
            now = datetime.now()
            state.is_playing = False
            state.last_play_command = None

            # Calculate playback duration if start time is available
            if 'play_start_time' in state.performance_metrics:
                start_time = datetime.fromisoformat(state.performance_metrics['play_start_time'])
                duration = (now - start_time).total_seconds()
                state.performance_metrics['playback_duration'] = duration
                result.metadata['playback_duration'] = duration

            state.performance_metrics['last_stop_time'] = now.isoformat()
            state.performance_metrics['stop_reasoning'] = result.reasoning

            # Add to operation history
            operation_entry = {
                'timestamp': now.isoformat(),
                'operation': 'stop',
                'track': state.track_path,
                'duration': duration if 'duration' in locals() else None,
                'reasoning': result.reasoning,
                'feedback_score': result.feedback_score
            }
            state.operation_history.append(operation_entry)

            result.success = True
            result.metadata['energy_context'] = crowd_energy_context
            result.metadata['track_duration'] = duration if 'duration' in locals() else 0

            logger.info(
                f"Deck {deck_id} stopped (duration: {duration if 'duration' in locals() else 'unknown':.1f}s, "
                f"timing confidence: {timing_analysis.get('confidence', 0):.2f})",
                extra={
                    'deck': deck_id,
                    'duration': duration if 'duration' in locals() else 0,
                    'timing_confidence': timing_analysis.get('confidence', 0),
                    'reasoning': result.reasoning
                }
            )

            # Log successful operation to learning system
            log_deck_operation(result)
            provide_master_coordinator_feedback(result, get_all_deck_states())

        else:
            result.success = False
            result.reasoning = "MIDI command failed to stop deck"
            result.feedback_score = 0.0

            raise RuntimeError(f"Failed to send stop command to deck {deck_id}")

        return success

    except Exception as e:
        result.success = False
        result.reasoning = f"Failed to stop deck: {str(e)}"
        result.feedback_score = 0.0

        logger.error(
            f"Failed to stop Deck {deck_id}: {str(e)}",
            extra={'deck': deck_id, 'error': str(e)}
        )

        # Log failed operation to learning system
        log_deck_operation(result)
        provide_master_coordinator_feedback(result, get_all_deck_states())

        raise


def play_deck(deck_id: str, track_path: str, is_first_track: bool = False,
               context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Play track on specified deck with DJ workflow compliance and persistent learning

    This function implements CRITICAL DJ workflow rules from DJ_WORKFLOW_RULES.md
    and enhances them with learning from past successful operations:

    1. Query knowledge base for optimal timing and volume decisions
    2. Check if ANY deck is currently playing
    3. Apply MASTER/SYNC logic with learned optimizations
    4. Log operation decisions for future learning
    5. Provide feedback to master coordinator

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')
        track_path: Path to track file (for loading)
        is_first_track: Force first-track behavior (MASTER, no SYNC)
        context: Current DJ context (genre, energy, crowd response) for learning

    Returns:
        True on success

    Raises:
        RuntimeError: If MIDI communication fails
        ValueError: If invalid deck_id

    Example:
        >>> # First track of session with learning
        >>> play_deck('A', '/path/to/track1.mp3', is_first_track=True,
        ...          context={'genre': 'techno', 'energy': 'building'})

        >>> # Second track with crowd energy context
        >>> play_deck('B', '/path/to/track2.mp3',
        ...          context={'transition_smooth': True, 'crowd_energy': 'high'})
    """
    if context is None:
        context = {}

    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be A, B, C, or D")

    state = _deck_states[deck_id]
    current_system_state = get_all_deck_states()

    result = DeckOperationResult(
        operation_type='play',
        deck_id=deck_id,
        success=False,
        track_path=track_path,
        reasoning=""
    )

    try:
        # ========================================================================
        # QUERY KNOWLEDGE BASE FOR OPTIMAL PLAYBACK DECISIONS
        # ========================================================================
        playback_optimal = query_playback_optimal_decision(deck_id, track_path, current_system_state)
        optimal_volume = playback_optimal.get('optimal_volume', 0.85)
        should_be_master = playback_optimal.get('should_be_master', True)
        should_enable_sync = playback_optimal.get('should_enable_sync', False)
        decision_confidence = playback_optimal.get('confidence', 0.0)
        learning_reasoning = playback_optimal.get('reasoning', 'Rule-based decision')

        result.metadata['learning_confidence'] = decision_confidence
        result.metadata['optimal_volume'] = optimal_volume
        result.metadata['should_be_master'] = should_be_master
        result.metadata['should_enable_sync'] = should_enable_sync

        # ========================================================================
        # ANTI-BLINKING LED LOGIC
        # ========================================================================
        current_time = time.time() * 1000  # Convert to milliseconds

        if state.last_play_command:
            elapsed = current_time - state.last_play_command
            if elapsed < DEBOUNCE_MS:
                result.reasoning = f"Ignoring rapid play command (debounce: {elapsed:.1f}ms)"
                result.feedback_score = 0.5  # Partial credit for preventing blinks

                logger.debug(
                    f"Ignoring rapid play command on Deck {deck_id} (debounce)",
                    extra={'deck': deck_id, 'elapsed_ms': elapsed}
                )

                # Log debounce action to learning system
                log_deck_operation(result)
                return True  # Ignore rapid commands

        # ========================================================================
        # LOAD TRACK WITH LEARNING CONTEXT
        # ========================================================================
        transition_context = {
            'genre': context.get('genre', 'unknown'),
            'energy_level': context.get('energy', 'unknown'),
            'transition_type': context.get('transition_type', 'start'),
            'crowd_response': context.get('crowd_response', 'neutral')
        }

        try:
            load_track(deck_id, track_path, transition_context)
        except FileNotFoundError as e:
            result.reasoning = f"Cannot play deck - track not found: {str(e)}"
            result.feedback_score = 0.0

            logger.error(f"Cannot play deck: {str(e)}")
            log_deck_operation(result)
            provide_master_coordinator_feedback(result, current_system_state)
            raise

        # ========================================================================
        # DJ WORKFLOW RULE #1: MASTER vs SYNC DECISION (Enhanced with Learning)
        # ========================================================================
        any_playing = check_any_deck_playing()
        master_deck = get_master_deck()

        # Base decision from DJ workflow rules
        if is_first_track or not any_playing:
            workflow_decision = {
                'should_be_master': True,
                'should_enable_sync': False,
                'volume': 0.85,
                'reason': 'first_track_scenario'
            }
        else:
            workflow_decision = {
                'should_be_master': False,
                'should_enable_sync': True,
                'volume': 0.20,
                'reason': f'subsequent_track_sync_to_{master_deck}'
            }

        # Merge workflow rules with learned optimizations
        # Learning overrides only if confidence > 0.7
        if decision_confidence > 0.7:
            # Use learned decisions
            final_master = should_be_master
            final_sync = should_enable_sync
            final_volume = optimal_volume
            reasoning = f"Learned optimization: {learning_reasoning} (confidence: {decision_confidence:.2f})"
        else:
            # Use workflow rules with learning influence if available
            final_master = workflow_decision['should_be_master']
            final_sync = workflow_decision['should_enable_sync']
            # Blend volumes: 70% workflow, 30% learning
            final_volume = (workflow_decision['volume'] * 0.7 + optimal_volume * 0.3)
            reasoning = f"DJ workflow: {workflow_decision['reason']}"
            if decision_confidence > 0.3:
                reasoning += f" (learning influence: {learning_reasoning})"

        # Apply the decisions
        if final_master:
            set_deck_master(deck_id, True)
        else:
            set_deck_master(deck_id, False)

        if final_sync:
            set_deck_sync(deck_id, True)
        else:
            set_deck_sync(deck_id, False)

        set_deck_volume(deck_id, final_volume)

        # Store decisions in result metadata
        result.metadata['final_master'] = final_master
        result.metadata['final_sync'] = final_sync
        result.metadata['final_volume'] = final_volume
        result.reasoning = reasoning

        # ========================================================================
        # SEND PLAY COMMAND
        # ========================================================================
        cc_number = DECK_CC_MAP[deck_id]['play']
        success = send_midi_cc(cc_number, 127)

        if success:
            # Update state with detailed timing information
            now = datetime.now()
            state.is_playing = True
            state.last_play_command = current_time
            state.performance_metrics['play_start_time'] = now.isoformat()
            state.performance_metrics['play_confidence'] = decision_confidence
            state.performance_metrics['play_reasoning'] = reasoning
            state.performance_metrics['used_learning'] = decision_confidence > 0.7

            # Add to operation history
            operation_entry = {
                'timestamp': now.isoformat(),
                'operation': 'play',
                'track': track_path,
                'master': final_master,
                'sync': final_sync,
                'volume': final_volume,
                'reasoning': reasoning,
                'learning_confidence': decision_confidence,
                'context': context
            }
            state.operation_history.append(operation_entry)

            result.success = True
            result.feedback_score = 0.9 if decision_confidence > 0.5 else 0.7
            result.metadata['play_start_time'] = now.isoformat()
            result.metadata['context'] = context

            logger.info(
                f"Deck {deck_id} now playing: {Path(track_path).name} "
                f"(MASTER:{final_master} SYNC:{final_sync} VOL:{final_volume:.2f} "
                f"LEARN:{decision_confidence:.2f})",
                extra={
                    'deck': deck_id,
                    'track': track_path,
                    'is_master': final_master,
                    'is_sync': final_sync,
                    'volume': final_volume,
                    'learning_confidence': decision_confidence,
                    'reasoning': reasoning
                }
            )

            # Log successful operation to learning system
            log_deck_operation(result)
            provide_master_coordinator_feedback(result, current_system_state)

        else:
            result.success = False
            result.reasoning = "MIDI command failed to start playback"
            result.feedback_score = 0.0

            raise RuntimeError(f"Failed to send play command to deck {deck_id}")

        return success

    except Exception as e:
        result.success = False
        result.reasoning = f"Failed to play deck: {str(e)}"
        result.feedback_score = 0.0

        logger.error(
            f"Failed to play Deck {deck_id}: {str(e)}",
            extra={'deck': deck_id, 'track_path': track_path, 'error': str(e)}
        )

        # Log failed operation to learning system
        log_deck_operation(result)
        provide_master_coordinator_feedback(result, current_system_state)

        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_all_deck_states() -> Dict[str, Dict[str, Any]]:
    """
    Get states of all four decks with learning insights

    Returns:
        Dictionary mapping deck_id to state dict including performance metrics

    Example:
        >>> states = get_all_deck_states()
        >>> for deck_id, state in states.items():
        ...     print(f"Deck {deck_id}: {state['is_playing']}")
    """
    states = {}
    for deck_id in ['A', 'B', 'C', 'D']:
        deck_state = get_deck_state(deck_id)
        # Add learning-specific information
        deck_state['operation_history_count'] = len(_deck_states[deck_id].operation_history)
        deck_state['performance_metrics'] = _deck_states[deck_id].performance_metrics
        deck_state['learning_enabled'] = PERSISTENT_LEARNING_ENABLED
        states[deck_id] = deck_state
    return states


def get_deck_learning_insights(deck_id: str) -> Dict[str, Any]:
    """
    Get learning insights and recommendations for a specific deck

    Args:
        deck_id: Deck identifier ('A', 'B', 'C', 'D')

    Returns:
        Dictionary with learning insights and recommendations
    """
    if deck_id not in ['A', 'B', 'C', 'D']:
        raise ValueError(f"Invalid deck_id: {deck_id}. Must be A, B, C, or D")

    state = _deck_states[deck_id]

    insights = {
        'learning_enabled': PERSISTENT_LEARNING_ENABLED,
        'total_operations': len(state.operation_history),
        'current_performance': state.performance_metrics,
        'recommendations': []
    }

    if not PERSISTENT_LEARNING_ENABLED:
        insights['status'] = 'Learning disabled - persistent learning not available'
        return insights

    # Analyze operation history for patterns
    if state.operation_history:
        recent_ops = state.operation_history[-10:]  # Last 10 operations

        # Calculate average feedback scores
        play_scores = [op['feedback_score'] for op in recent_ops if op.get('operation') == 'play']
        stop_scores = [op['feedback_score'] for op in recent_ops if op.get('operation') == 'stop']

        if play_scores:
            insights['avg_play_success'] = sum(play_scores) / len(play_scores)
            if insights['avg_play_success'] < 0.7:
                insights['recommendations'].append("Consider reviewing track selection timing")

        if stop_scores:
            insights['avg_stop_success'] = sum(stop_scores) / len(stop_scores)
            if insights['avg_stop_success'] < 0.7:
                insights['recommendations'].append("Review stop timing for better crowd response")

    # Generate recommendations based on current state
    if state.is_playing:
        if 'play_confidence' in state.performance_metrics:
            confidence = state.performance_metrics['play_confidence']
            if confidence < 0.5:
                insights['recommendations'].append("Low confidence in current playback - consider manual review")
            else:
                insights['recommendations'].append(f"Strong playback decision (confidence: {confidence:.2f})")

    insights['status'] = f"Learning active with {len(state.operation_history)} operations recorded"
    return insights


def reset_all_decks() -> bool:
    """
    Stop all decks and reset to initial state

    Returns:
        True on success
    """
    logger.info("Resetting all decks to initial state")

    success = True
    for deck_id in ['A', 'B', 'C', 'D']:
        try:
            stop_deck(deck_id)
            set_deck_master(deck_id, False)
            set_deck_sync(deck_id, False)
            set_deck_volume(deck_id, 0.85)

            # Reset state
            _deck_states[deck_id] = DeckState(deck_id=deck_id)

        except Exception as e:
            logger.error(
                f"Failed to reset Deck {deck_id}: {str(e)}",
                extra={'deck': deck_id, 'error': str(e)}
            )
            success = False

    return success


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

def initialize_deck_operations():
    """
    Initialize deck operations module with persistent learning support

    - Initialize MIDI driver
    - Reset all decks to known state
    - Configure logging
    - Initialize persistent learning system if available
    """
    logger.info("Initializing deck operations module (v2.0.0 with persistent learning)")

    # Report learning system status
    if PERSISTENT_LEARNING_ENABLED:
        try:
            memory_system = get_memory_system()
            stats = memory_system.get_memory_stats()
            logger.info(
                f"Persistent learning enabled: {stats['knowledge_entries']} knowledge entries, "
                f"{stats['conversation_messages']} conversation messages"
            )
        except Exception as e:
            logger.warning(f"Learning enabled but stats unavailable: {e}")
    else:
        logger.info("Persistent learning disabled - running in basic mode")

    # Initialize MIDI driver (ensures connection on startup)
    try:
        get_midi_driver()
        logger.info("MIDI driver initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MIDI driver: {str(e)}")
        raise

    # Reset all decks
    reset_all_decks()

    logger.info("Deck operations module initialized successfully with learning capabilities")


# ============================================================================
# MAIN ENTRY POINT (For Testing)
# ============================================================================

if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize module
    initialize_deck_operations()

    # Print all deck states
    print("\n=== ALL DECK STATES ===")
    states = get_all_deck_states()
    for deck_id, state in states.items():
        print(f"Deck {deck_id}: {state}")

    print("\n=== DECK OPERATIONS MODULE READY ===")
