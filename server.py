"""
FastAPI Server per DJ AI.
Fornisce REST API + WebSocket per front-end.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import sys
from pathlib import Path
import os

# Add autonomous_dj to path
sys.path.insert(0, str(Path(__file__).parent))
os.chdir(Path(__file__).parent)

# Import controller (only when all dependencies available)
try:
    from autonomous_dj.workflow_controller import DJWorkflowController
    CONTROLLER_AVAILABLE = True
except ImportError as e:
    print(f"WARNING:  Warning: Controller not available: {e}")
    print("WARNING:  Server will run in demo mode without Traktor integration")
    CONTROLLER_AVAILABLE = False
    DJWorkflowController = None

# Init FastAPI
app = FastAPI(
    title="DJ AI Server",
    description="Autonomous DJ System with AI Vision Control",
    version="1.0.0"
)

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init controller (if available)
controller = None
if CONTROLLER_AVAILABLE:
    try:
        controller = DJWorkflowController()
    except Exception as e:
        print(f"WARNING:  Warning: Could not initialize controller: {e}")
        print("WARNING:  Server will run in demo mode")

# Models
class CommandRequest(BaseModel):
    command: str

# REST Endpoints
@app.get("/")
async def root():
    """Redirect to frontend."""
    return FileResponse("frontend/index.html")

@app.post("/api/command")
async def execute_command(req: CommandRequest):
    """Esegue comando utente."""

    if not controller:
        # Demo mode response
        return {
            'success': False,
            'response': f"Demo mode: Ricevuto comando '{req.command}' ma controller non disponibile. "
                       f"Configura API keys e riavvia server.",
            'action_taken': 'demo',
            'new_state': {}
        }

    result = controller.handle_user_command(req.command)
    return result

@app.get("/api/status")
async def get_status():
    """Ritorna stato corrente."""

    if not controller:
        # Demo mode state
        return {
            'browser': {'track_highlighted': 'Demo Mode - No Traktor Connection'},
            'deck_a': {'status': 'disconnected'},
            'deck_b': {'status': 'disconnected'},
            'mixer': {},
            'mode': 'demo',
            'last_update': 0
        }

    return controller.get_current_state()

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        'status': 'ok',
        'controller_available': controller is not None,
        'mode': 'production' if controller else 'demo'
    }

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket per aggiornamenti real-time stato Traktor."""
    await websocket.accept()

    print("[WS] Client connected")

    try:
        while True:
            if controller:
                # Refresh and send state
                controller.refresh_state()
                state = controller.get_current_state()
            else:
                # Demo mode state
                state = {
                    'browser': {'track_highlighted': 'Demo Mode'},
                    'deck_a': {'status': 'disconnected'},
                    'deck_b': {'status': 'disconnected'},
                    'mixer': {},
                    'mode': 'demo',
                    'last_update': 0
                }

            await websocket.send_json(state)

            # Update every 2 seconds
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        print(f"[WS] Error: {e}")

# Serve front-end static files
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
else:
    print(f"WARNING:  Warning: Frontend directory not found at {frontend_path}")
    print("WARNING:  Create frontend/ directory with index.html")

# Startup
@app.on_event("startup")
async def startup():
    print("=" * 70)
    print(" DJ AI SERVER STARTED")
    print("=" * 70)
    print(f"Mode: {'PRODUCTION' if controller else 'DEMO'}")
    print(f"Frontend: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"Health: http://localhost:8000/api/health")
    print("=" * 70)

    if not controller:
        print("")
        print("WARNING:  WARNING: Running in DEMO mode!")
        print("WARNING:  To enable full functionality:")
        print("   1. Configure autonomous_dj/config.py with your API keys")
        print("   2. Ensure Traktor Pro 3 is running")
        print("   3. Verify loopMIDI is configured")
        print("   4. Restart server")
        print("=" * 70)

# Shutdown
@app.on_event("shutdown")
async def shutdown():
    if controller:
        controller.cleanup()
    print("\n Server shutdown")

# Run with: uvicorn server:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
