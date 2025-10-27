# 💻 Development Guide - Traktor AI

Guida per sviluppatori che vogliono contribuire o estendere il sistema Traktor AI.

---

## 📋 Indice

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Code Style](#code-style)
4. [Testing](#testing)
5. [Adding Features](#adding-features)
6. [MIDI Mappings](#midi-mappings)
7. [Database Schema](#database-schema)
8. [API Development](#api-development)
9. [Contributing Guidelines](#contributing-guidelines)

---

## 1. Development Setup

### Prerequisites

- Python 3.8+
- Git
- Traktor Pro 3
- loopMIDI (Windows) / IAC Driver (macOS)
- Code editor (VS Code raccomandato)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/Fiore0312/traktor.git
cd traktor

# Create virtual environment
python -m venv venv

# Activate
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies (with dev tools)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Or install dev dependencies manually
pip install pytest pytest-asyncio black flake8 mypy

# Setup pre-commit hooks
pip install pre-commit
pre-commit install
```

### VS Code Setup

**Recommended extensions**:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-vscode.test-adapter-converter",
    "njpwerner.autodocstring"
  ]
}
```

**Settings** (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

---

## 2. Project Structure

```
traktor/
├── autonomous_dj/               # Core system modules
│   ├── __init__.py
│   ├── config.py                # User config (NOT in git)
│   ├── config.template.py       # Template for config
│   ├── openrouter_client.py     # LLM client
│   ├── workflow_controller.py   # Main orchestrator
│   ├── traktor_vision.py        # Screenshot capture
│   └── claude_vision_client.py  # Vision API client
│
├── config/                      # Configuration files
│   ├── traktor_midi_mapping.json      # MIDI CC mappings
│   ├── keyboard_shortcuts_mapping.json
│   └── config_loader.py         # Config loader utility
│
├── camelot_matcher.py           # Camelot Wheel algorithm
├── collection_parser_xml.py     # Traktor collection parser
├── midi_navigator.py            # MIDI browser navigation
├── traktor_midi_driver.py       # MIDI driver
├── traktor_safety_checks.py     # Safety validation layer
│
├── frontend/                    # Web interface
│   ├── index.html               # Main UI
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── templates/
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── test_midi_driver.py
│   ├── test_camelot_matcher.py
│   ├── test_collection_parser.py
│   ├── test_api.py
│   └── test_integration.py
│
├── docs/                        # Documentation
│   ├── SETUP.md
│   ├── INTEGRATION_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── CAMELOT_WHEEL_GUIDE.md
│   ├── VISION_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── DEVELOPMENT.md           # This file
│
├── data/                        # Runtime data (NOT in git)
│   ├── screenshots/
│   ├── logs/
│   └── backups/
│
├── tracks.db                    # SQLite database
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Dev dependencies
├── .gitignore
├── .pre-commit-config.yaml
├── pytest.ini
├── README.md
└── CLAUDE.md                    # Project context for Claude Code
```

---

## 3. Code Style

### Python Style Guide

**Follow PEP 8** with some customizations:

```python
# Line length: 100 characters (not 79)
# Use Black formatter with this config:

# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
```

### Naming Conventions

```python
# Functions: snake_case
def find_compatible_tracks(current_key: str) -> List[Track]:
    pass

# Classes: PascalCase
class CamelotMatcher:
    pass

# Constants: UPPER_SNAKE_CASE
MIDI_PORT_NAME = "Traktor MIDI Bus 1"
DEFAULT_BPM = 128.0

# Private methods: _leading_underscore
def _internal_helper(self):
    pass
```

### Type Hints

**Always use type hints**:

```python
from typing import List, Dict, Optional, Tuple

def parse_collection(
    collection_path: str,
    output_db: Optional[str] = None
) -> Tuple[int, List[str]]:
    """
    Parse Traktor collection.nml file.

    Args:
        collection_path: Path to collection.nml
        output_db: Optional output database path

    Returns:
        Tuple of (tracks_count, errors_list)

    Raises:
        FileNotFoundError: If collection.nml not found
        ValueError: If XML parsing fails
    """
    pass
```

### Docstrings

**Use Google-style docstrings**:

```python
def calculate_compatibility_score(
    current_key: str,
    current_bpm: float,
    candidate_key: str,
    candidate_bpm: float
) -> int:
    """Calculate compatibility score for track pairing.

    Uses Camelot Wheel rules for key matching and BPM tolerance
    for tempo matching. Scores range from 0 (incompatible) to 15
    (perfect match).

    Args:
        current_key: Camelot key of current track (e.g., "8A")
        current_bpm: BPM of current track (e.g., 128.0)
        candidate_key: Camelot key of candidate track
        candidate_bpm: BPM of candidate track

    Returns:
        Compatibility score (0-15)

    Example:
        >>> calculate_compatibility_score("8A", 128.0, "8B", 128.5)
        15

    Note:
        Key score contributes 0-10 points, BPM score 0-5 points
    """
    # Implementation
```

---

## 4. Testing

### Test Structure

```python
# tests/test_camelot_matcher.py

import pytest
from camelot_matcher import CamelotMatcher, Track

@pytest.fixture
def matcher():
    """Fixture providing CamelotMatcher instance."""
    return CamelotMatcher(db_path=":memory:")

@pytest.fixture
def sample_tracks():
    """Fixture providing sample tracks for testing."""
    return [
        Track(id=1, title="Track 1", key="8A", bpm=128.0),
        Track(id=2, title="Track 2", key="8B", bpm=128.5),
        Track(id=3, title="Track 3", key="9A", bpm=130.0),
    ]

def test_find_compatible_tracks_same_hour(matcher, sample_tracks):
    """Test finding tracks with same hour, different letter."""
    matcher.load_tracks(sample_tracks)

    compatible = matcher.find_compatible("8A", 128.0)

    assert len(compatible) > 0
    assert compatible[0].key == "8B"
    assert compatible[0].id == 2

def test_bpm_range_calculation(matcher):
    """Test BPM range calculation with default tolerance."""
    min_bpm, max_bpm = matcher.calculate_bpm_range(128.0)

    assert min_bpm == pytest.approx(120.32)
    assert max_bpm == pytest.approx(135.68)
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_camelot_matcher.py

# Run specific test
pytest tests/test_camelot_matcher.py::test_find_compatible_tracks_same_hour

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Integration Tests

```python
# tests/test_integration.py

def test_end_to_end_workflow(traktor_running):
    """Test complete workflow from command to MIDI execution."""

    # 1. Send natural language command
    response = requests.post(
        'http://localhost:8000/api/chat',
        json={'message': 'trova traccia compatibile'}
    )

    assert response.status_code == 200
    result = response.json()

    # 2. Verify command parsed
    assert result['command'] == 'FIND_COMPATIBLE_TRACK'

    # 3. Verify track found
    assert 'track' in result['result']
    track = result['result']['track']

    # 4. Verify Camelot match
    assert track['key'] in ['7A', '8A', '8B', '9A']

    # 5. Verify MIDI sent (check logs)
    # Implementation depends on logging setup
```

---

## 5. Adding Features

### Example: Add New MIDI Command

**Step 1**: Add CC mapping

```json
// config/traktor_midi_mapping.json
{
  "deck_operations": {
    "cue_point_1": {
      "cc": 30,
      "value": 127,
      "deck_a": 30,
      "deck_b": 31
    }
  }
}
```

**Step 2**: Add method to MIDI driver

```python
# traktor_midi_driver.py

def trigger_cue_point(self, deck: str, cue_number: int):
    """Trigger cue point on specified deck.

    Args:
        deck: "A" or "B"
        cue_number: 1-8
    """
    cc_base = 30  # Cue 1 on Deck A
    cc_offset = 0 if deck == "A" else 1
    cc_number = cc_base + (cue_number - 1) * 2 + cc_offset

    self.send_cc(cc_number, 127)
    logger.info(f"Triggered cue {cue_number} on Deck {deck}")
```

**Step 3**: Add API endpoint

```python
# workflow_controller.py

@app.route('/api/trigger-cue', methods=['POST'])
def api_trigger_cue():
    """Trigger cue point via API."""
    data = request.json
    deck = data.get('deck', 'A')
    cue = data.get('cue', 1)

    midi_driver.trigger_cue_point(deck, cue)

    return jsonify({
        'status': 'success',
        'deck': deck,
        'cue': cue
    })
```

**Step 4**: Add tests

```python
# tests/test_midi_driver.py

def test_trigger_cue_point(midi_driver):
    """Test cue point triggering."""
    midi_driver.trigger_cue_point("A", 1)

    # Verify MIDI message sent
    # (Implementation depends on mocking setup)
```

### Example: Add New Camelot Rule

```python
# camelot_matcher.py

def get_compatible_keys_extended(current_key: str) -> List[Tuple[str, int]]:
    """Extended compatibility with diagonal moves."""

    compatible = get_compatible_keys(current_key)  # Existing rules

    # Add diagonal moves (experimental)
    number = int(current_key[:-1])
    letter = current_key[-1]

    # +1 hour, opposite letter (energy boost + mode change)
    next_hour = 1 if number == 12 else number + 1
    opposite = 'B' if letter == 'A' else 'A'
    diagonal = f"{next_hour}{opposite}"

    compatible.append((diagonal, 6))  # Lower score (experimental)

    return compatible
```

---

## 6. MIDI Mappings

### Adding New Mapping

**Process**:

1. **Traktor side**:
   ```
   Preferences → Controller Manager → Add In/Out
   → Assign function
   → Note CC number
   ```

2. **JSON config**:
   ```json
   // config/traktor_midi_mapping.json
   {
     "new_category": {
       "new_function": {
         "cc": 40,
         "value": 127
       }
     }
   }
   ```

3. **Python code**:
   ```python
   # config_loader.py
   mapping = load_midi_mapping()
   cc = mapping['new_category']['new_function']['cc']
   ```

4. **Export TSI**:
   ```
   Traktor → Controller Manager
   → Export → Save as TraktorMIDIMapping.tsi
   → Place in config/
   ```

---

## 7. Database Schema

### Current Schema

```sql
-- tracks table
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT,
    bpm REAL NOT NULL,
    key TEXT NOT NULL,
    path TEXT UNIQUE NOT NULL,
    duration INTEGER,
    genre TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_key ON tracks(key);
CREATE INDEX idx_bpm ON tracks(bpm);
CREATE INDEX idx_key_bpm ON tracks(key, bpm);
```

### Adding New Table

```python
# collection_parser_xml.py

def create_database_schema(conn):
    """Create database tables and indexes."""

    # Existing tracks table
    # ...

    # New table: playlists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS playlist_tracks (
            playlist_id INTEGER,
            track_id INTEGER,
            position INTEGER,
            FOREIGN KEY (playlist_id) REFERENCES playlists(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id),
            PRIMARY KEY (playlist_id, track_id)
        )
    """)
```

---

## 8. API Development

### Adding New Endpoint

```python
# workflow_controller.py

@app.route('/api/get-deck-state', methods=['GET'])
def api_get_deck_state():
    """Get current state of specified deck.

    Query params:
        deck (str): "A" or "B"

    Returns:
        JSON with deck state (BPM, key, playing status)
    """
    deck = request.args.get('deck', 'A')

    if config.USE_VISION:
        state = vision_system.get_deck_state(deck)
    else:
        state = {
            'deck': deck,
            'bpm': 128.0,
            'key': '8A',
            'playing': False,
            'mode': 'blind'
        }

    return jsonify(state)
```

### WebSocket Event

```python
# workflow_controller.py

from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('request_deck_state')
def handle_deck_state_request(data):
    """Handle WebSocket request for deck state."""
    deck = data.get('deck', 'A')
    state = get_deck_state(deck)

    emit('deck_state_update', {
        'deck': deck,
        'state': state,
        'timestamp': time.time()
    })
```

---

## 9. Contributing Guidelines

### Pull Request Process

1. **Fork repository**
   ```bash
   # On GitHub: click "Fork"
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/traktor.git
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Run tests**
   ```bash
   pytest
   black .
   flake8 .
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   **Commit message format**:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `test:` adding tests
   - `refactor:` code refactoring

6. **Push**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Describe changes
   - Link related issues

### Code Review Checklist

- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Commit messages clear
- [ ] No hardcoded values (use config)
- [ ] Error handling present
- [ ] Logging added where appropriate

---

## 📚 Resources

- **Python Docs**: https://docs.python.org/3/
- **Flask Docs**: https://flask.palletsprojects.com/
- **pytest Docs**: https://docs.pytest.org/
- **Black**: https://black.readthedocs.io/
- **MIDI Spec**: https://www.midi.org/specifications

---

## 📞 Developer Support

- **GitHub Issues**: https://github.com/Fiore0312/traktor/issues
- **Discussions**: https://github.com/Fiore0312/traktor/discussions
- **Wiki**: https://github.com/Fiore0312/traktor/wiki

---

**Happy coding!** 🎉

*Last updated: October 26, 2025*
