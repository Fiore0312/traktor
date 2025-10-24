"""
Configuration Template - DJ AI System
COPY THIS FILE TO config.py AND ADD YOUR API KEYS

⚠️ IMPORTANT:
- DO NOT commit config.py to git (it's in .gitignore)
- NEVER share your API keys publicly
"""

import os

# ============================================================================
# ⚠️ API KEYS - REPLACE WITH YOUR ACTUAL KEYS
# ============================================================================

# ANTHROPIC API (Claude Vision)
# Get from: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY = "your-anthropic-api-key-here"

# OPENROUTER API (Alternative/Backup)
# Get from: https://openrouter.ai/keys
OPENROUTER_API_KEY = "your-openrouter-api-key-here"

# ============================================================================
# AI MODEL CONFIGURATION
# ============================================================================

# Claude Vision
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# OpenRouter model (if using)
AI_MODEL = "google/gemini-2.0-flash-exp:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ============================================================================
# PROVIDER SELECTION
# ============================================================================

USE_CLAUDE_FOR_VISION = True
USE_OPENROUTER = False

# ============================================================================
# AI PARAMETERS
# ============================================================================

CLAUDE_TEMPERATURE = 0.2
CLAUDE_MAX_TOKENS = 2000
CLAUDE_TIMEOUT = 30

AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 2000
AI_TIMEOUT = 30

# ============================================================================
# FEATURE FLAGS
# ============================================================================

USE_AI_FOR_VISION_ANALYSIS = True
USE_AI_FOR_TRACK_SELECTION = False
USE_AI_FOR_MIX_DECISIONS = False

# ============================================================================
# TRAKTOR PATHS
# ============================================================================

TRAKTOR_COLLECTION_PATH = r"C:\Users\Utente\Documents\Native Instruments\Traktor 3.11.1\collection.nml"
SCREENSHOT_DIR = r"C:\traktor\data\screenshots"
BACKUP_DIR = r"C:\traktor\data\backups"

# ============================================================================
# MIDI CONFIGURATION
# ============================================================================

MIDI_PORT_NAME = "Traktor MIDI Bus 1"
MIDI_DRY_RUN = False

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FILE = r"C:\traktor\data\logs\autonomous_dj.log"
LOG_MAX_SIZE_MB = 10

# ============================================================================
# VISION SYSTEM
# ============================================================================

SCREENSHOT_QUALITY = 95
SCREENSHOT_INTERVAL = 5

# ============================================================================
# SAFETY DEFAULTS
# ============================================================================

SAFE_VOLUME_DEFAULT = 0
SAFE_GAIN_DEFAULT = 64
SAFE_EQ_HI_DEFAULT = 64
SAFE_EQ_MID_DEFAULT = 64
SAFE_EQ_LOW_DEFAULT = 64
SAFE_FILTER_DEFAULT = 64
SAFE_CROSSFADER_DEFAULT = 64

# ============================================================================
# DECK CONFIGURATION
# ============================================================================

DECK_A = 'A'
DECK_B = 'B'
DECK_C = 'C'
DECK_D = 'D'

# ============================================================================
# TIMING
# ============================================================================

MIDI_COMMAND_DELAY = 0.05  # 50ms between MIDI commands
BROWSER_NAVIGATION_DELAY = 1.5  # 1.5s for browser navigation
DECK_LOAD_DELAY = 2.0  # 2s after loading track

# ============================================================================
# WORKFLOW
# ============================================================================

AUTO_SYNC_ENABLED = True
AUTO_MASTER_TRANSFER = True
PRE_PLAYBACK_MIXER_SETUP = True

# ============================================================================
# OPENROUTER METADATA (if using OpenRouter)
# ============================================================================

OPENROUTER_SITE_URL = "https://github.com/yourusername/traktor"
OPENROUTER_APP_NAME = "Traktor AI"
