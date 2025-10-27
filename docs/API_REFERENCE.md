# 🌐 API Reference - Traktor AI

Documentazione completa delle API REST e WebSocket del sistema Traktor AI.

**Base URL**: `http://localhost:8000`

---

## 📋 Endpoints Overview

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/` | GET | No | Serve web interface |
| `/api/chat` | POST | No | Process natural language command |
| `/api/auto-select-track` | POST | No | Instant compatible track selection |
| `/api/status` | GET | No | System health check |
| `/api/tracks` | GET | No | List all tracks in database |
| `/api/tracks/:id` | GET | No | Get specific track details |
| `/api/compatible-tracks` | GET | No | Find compatible tracks |
| `/api/config` | GET/POST | No | Get/set system configuration |
| `/ws` | WebSocket | No | Real-time bidirectional updates |

---

## 📡 REST API

### 1. Chat Interface

**Process natural language command**

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Trova una traccia compatibile in D major"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "command": "FIND_COMPATIBLE_TRACK",
  "result": {
    "track": {
      "title": "Techno Track 001",
      "artist": "DJ Fiore",
      "bpm": 128.0,
      "key": "8A",
      "path": "Techno/DJ Fiore/Track001.mp3"
    },
    "loaded_on_deck": "B"
  },
  "message": "Traccia compatibile caricata su Deck B"
}
```

**Supported Commands**:
- `"Trova una traccia compatibile"` → FIND_COMPATIBLE_TRACK
- `"Carica traccia su Deck A"` → LOAD_TRACK
- `"Mixa Deck A e B"` → MIX_DECKS
- `"Analizza stato Traktor"` → GET_STATUS

---

### 2. Auto-Select Compatible Track

**Quick action: instant selection**

```http
POST /api/auto-select-track
Content-Type: application/json

{
  "deck": "B",
  "current_key": "8A",  // Optional (auto-detect if Vision enabled)
  "current_bpm": 128.0   // Optional
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "track": {
    "id": 42,
    "title": "Progressive House Anthem",
    "artist": "Various Artists",
    "bpm": 126.0,
    "key": "8B",
    "path": "House/Track042.mp3",
    "compatibility_score": 10
  },
  "current_state": {
    "bpm": 128.0,
    "key": "8A",
    "deck": "A"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "status": "error",
  "error": "NO_COMPATIBLE_TRACKS",
  "message": "Nessuna traccia compatibile trovata per 8A @ 128 BPM"
}
```

---

### 3. System Status

**Health check**

```http
GET /api/status
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T14:30:00Z",
  "components": {
    "midi_driver": {
      "status": "connected",
      "port": "Traktor MIDI Bus 1",
      "latency_ms": 8
    },
    "vision_system": {
      "status": "active",
      "mode": "blind",
      "last_capture": "2025-10-26T14:29:50Z"
    },
    "database": {
      "status": "online",
      "tracks_count": 393,
      "last_update": "2025-10-25T10:00:00Z"
    },
    "openrouter_client": {
      "status": "ready",
      "model": "deepseek/deepseek-chat"
    }
  },
  "uptime_seconds": 3600
}
```

---

### 4. List Tracks

**Get all tracks from database**

```http
GET /api/tracks?limit=50&offset=0&genre=Techno&sort=bpm
```

**Query Parameters**:
- `limit` (int): Max results (default: 100)
- `offset` (int): Pagination offset (default: 0)
- `genre` (string): Filter by genre (optional)
- `sort` (string): Sort field (`bpm`, `key`, `title`) (default: `title`)
- `order` (string): `asc` or `desc` (default: `asc`)

**Response** (200 OK):
```json
{
  "total": 393,
  "limit": 50,
  "offset": 0,
  "tracks": [
    {
      "id": 1,
      "title": "Techno Track 001",
      "artist": "DJ Fiore",
      "bpm": 128.0,
      "key": "8A",
      "genre": "Techno",
      "path": "Techno/Track001.mp3",
      "duration": 360
    },
    // ... 49 more tracks
  ]
}
```

---

### 5. Get Track Details

**Get specific track by ID**

```http
GET /api/tracks/42
```

**Response** (200 OK):
```json
{
  "id": 42,
  "title": "Progressive House Anthem",
  "artist": "Various Artists",
  "bpm": 126.0,
  "key": "8B",
  "key_musical": "C major",
  "genre": "House",
  "path": "House/Track042.mp3",
  "duration": 420,
  "compatible_keys": ["7B", "8B", "9B", "8A"],
  "compatible_tracks_count": 23,
  "metadata": {
    "bitrate": 320,
    "sample_rate": 44100,
    "format": "mp3"
  }
}
```

---

### 6. Find Compatible Tracks

**Query compatible tracks using Camelot Wheel**

```http
GET /api/compatible-tracks?key=8A&bpm=128&limit=10
```

**Query Parameters**:
- `key` (string): Camelot key (1A-12B) **required**
- `bpm` (float): Current BPM **required**
- `limit` (int): Max results (default: 10)
- `bpm_tolerance` (float): BPM range % (default: 6)

**Response** (200 OK):
```json
{
  "current_key": "8A",
  "current_bpm": 128.0,
  "bpm_range": {
    "min": 120.3,
    "max": 135.7
  },
  "compatible_tracks": [
    {
      "id": 15,
      "title": "Techno Anthem",
      "artist": "DJ X",
      "bpm": 128.0,
      "key": "8B",
      "compatibility_score": 10,
      "reason": "Same hour, different letter (perfect match)"
    },
    {
      "id": 23,
      "title": "Dark Techno",
      "artist": "DJ Y",
      "bpm": 127.5,
      "key": "9A",
      "compatibility_score": 8,
      "reason": "+1 hour, same letter"
    }
  ]
}
```

---

### 7. Configuration

**Get current config**

```http
GET /api/config
```

**Response** (200 OK):
```json
{
  "use_vision": false,
  "midi_port": "Traktor MIDI Bus 1",
  "server_host": "0.0.0.0",
  "server_port": 8000,
  "openrouter_model": "deepseek/deepseek-chat",
  "debug": true
}
```

**Update config**

```http
POST /api/config
Content-Type: application/json

{
  "use_vision": true,
  "debug": false
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Configuration updated",
  "updated_fields": ["use_vision", "debug"]
}
```

---

## 🔌 WebSocket API

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to Traktor AI');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### Message Types

#### 1. System Status Update

**Server → Client**:
```json
{
  "type": "status_update",
  "timestamp": "2025-10-26T14:30:00Z",
  "data": {
    "midi_connected": true,
    "tracks_loaded": 393,
    "vision_mode": "blind"
  }
}
```

#### 2. Track Loaded Event

**Server → Client**:
```json
{
  "type": "track_loaded",
  "timestamp": "2025-10-26T14:30:05Z",
  "data": {
    "deck": "B",
    "track": {
      "title": "Techno Track 001",
      "artist": "DJ Fiore",
      "bpm": 128.0,
      "key": "8A"
    }
  }
}
```

#### 3. Command Execution

**Server → Client**:
```json
{
  "type": "command_executed",
  "timestamp": "2025-10-26T14:30:10Z",
  "data": {
    "command": "FIND_COMPATIBLE_TRACK",
    "status": "success",
    "duration_ms": 850
  }
}
```

#### 4. Error Notification

**Server → Client**:
```json
{
  "type": "error",
  "timestamp": "2025-10-26T14:30:15Z",
  "data": {
    "error_code": "MIDI_CONNECTION_LOST",
    "message": "MIDI port disconnected",
    "severity": "high"
  }
}
```

#### 5. Send Command (Client → Server)

**Client → Server**:
```json
{
  "type": "command",
  "data": {
    "action": "find_compatible_track",
    "params": {
      "deck": "B"
    }
  }
}
```

---

## 🔐 Authentication (Future)

Currently **no authentication** required (localhost only).

**Planned**:
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "dj",
  "password": "secure_password"
}
```

**Response**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600
}
```

**Usage**:
```http
GET /api/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🧪 Testing API

### cURL Examples

```bash
# Chat command
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "trova traccia compatibile"}'

# Auto-select
curl -X POST http://localhost:8000/api/auto-select-track \
  -H "Content-Type: application/json" \
  -d '{"deck": "B"}'

# Get status
curl http://localhost:8000/api/status

# List tracks
curl "http://localhost:8000/api/tracks?limit=10&genre=Techno"

# Compatible tracks
curl "http://localhost:8000/api/compatible-tracks?key=8A&bpm=128"
```

### Python Example

```python
import requests

# Chat
response = requests.post(
    'http://localhost:8000/api/chat',
    json={'message': 'trova traccia compatibile'}
)
print(response.json())

# WebSocket
import websocket

def on_message(ws, message):
    print(f"Received: {message}")

ws = websocket.WebSocketApp(
    'ws://localhost:8000/ws',
    on_message=on_message
)
ws.run_forever()
```

---

## 📊 Rate Limits

**Current**: No rate limits (localhost)

**Planned** (for remote access):
- 100 requests/minute per IP
- 10 WebSocket connections per IP
- Burst: 20 requests in 1 second

---

*Last updated: October 26, 2025*
