"""
FastAPI Server per DJ AI - DEMO MODE
Server funzionante senza dipendenze da Traktor (per test frontend)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import time

# Init FastAPI
app = FastAPI(
    title="DJ AI Server (Demo Mode)",
    description="Autonomous DJ System - Demo Mode for Testing",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class CommandRequest(BaseModel):
    command: str

# Demo state
demo_state = {
    'browser': {'track_highlighted': 'Demo Track - Techno Mix.mp3'},
    'deck_a': {
        'status': 'loaded',
        'track_title': 'Underwater - Dub Techno',
        'playing': False
    },
    'deck_b': {
        'status': 'empty',
        'track_title': '',
        'playing': False
    },
    'mixer': {},
    'mode': 'demo',
    'last_update': time.time()
}

# REST Endpoints
@app.get("/")
async def root():
    """Serve frontend."""
    return FileResponse("frontend/index.html")

@app.post("/api/command")
async def execute_command(req: CommandRequest):
    """Handle user command (demo responses)."""

    command = req.command.lower()

    # Simple command responses
    if 'stato' in command or 'status' in command:
        response = """📊 STATO DEMO:

Browser: Demo Track - Techno Mix.mp3

Deck A: loaded
  Track: Underwater - Dub Techno
  Playing: No

Deck B: empty

Mode: DEMO (Configure API keys to enable full functionality)
"""

    elif 'carica' in command or 'load' in command:
        if 'a' in command.lower():
            demo_state['deck_a']['status'] = 'loaded'
            demo_state['deck_a']['track_title'] = 'Demo Track - Techno Mix'
            response = "✅ Demo: Track loaded on Deck A"
        else:
            demo_state['deck_b']['status'] = 'loaded'
            demo_state['deck_b']['track_title'] = 'Demo Track - House Groove'
            response = "✅ Demo: Track loaded on Deck B"

    elif 'play' in command:
        if 'a' in command.lower():
            demo_state['deck_a']['playing'] = True
            response = "▶️ Demo: Deck A playing"
        else:
            demo_state['deck_b']['playing'] = True
            response = "▶️ Demo: Deck B playing"

    elif 'pause' in command or 'stop' in command:
        if 'a' in command.lower():
            demo_state['deck_a']['playing'] = False
            response = "⏸ Demo: Deck A paused"
        else:
            demo_state['deck_b']['playing'] = False
            response = "⏸ Demo: Deck B paused"

    elif 'autonomo' in command or 'autonomous' in command:
        demo_state['mode'] = 'autonomous'
        response = "🤖 Demo: Autonomous mode activated (simulation only)"

    else:
        response = f"📝 Demo: Received command '{req.command}'\n\nTo enable full functionality:\n1. Configure autonomous_dj/config.py with API keys\n2. Start Traktor Pro 3\n3. Use server.py instead of server_demo.py"

    demo_state['last_update'] = time.time()

    return {
        'success': True,
        'response': response,
        'action_taken': 'demo',
        'new_state': demo_state
    }

@app.get("/api/status")
async def get_status():
    """Return current state."""
    return demo_state

@app.get("/api/health")
async def health_check():
    """Health check."""
    return {
        'status': 'ok',
        'controller_available': False,
        'mode': 'demo'
    }

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates."""
    await websocket.accept()
    print("[WS] Client connected")

    try:
        while True:
            demo_state['last_update'] = time.time()
            await websocket.send_json(demo_state)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("[WS] Client disconnected")

# Serve frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Startup
@app.on_event("startup")
async def startup():
    print("="*70)
    print("DJ AI SERVER - DEMO MODE")
    print("="*70)
    print("Frontend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("Health: http://localhost:8000/api/health")
    print("="*70)
    print("")
    print("Running in DEMO mode for frontend testing")
    print("Configure API keys and use server.py for full functionality")
    print("="*70)

# Run with: uvicorn server_demo:app --reload --port 8000
