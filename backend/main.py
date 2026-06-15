from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Annotated
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from database import Database
from models import ActionRequest, ActionResponse
from rules.orchestrator import Orchestrator

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "campaigns.db"

db = None
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db, orchestrator
    print("🎮 Starting Cripta...")
    db = Database(str(DB_PATH))
    await db.initialize()
    orchestrator = Orchestrator(db)
    print("✅ Ready!")
    yield
    if db:
        await db.close()
    print("🛑 Shutdown")

app = FastAPI(
    title="Cripta API",
    description="D&D 5.5 Virtual DM",
    version="0.1.0",
    lifespan=lifespan
)

# Parse CORS_ORIGINS from environment, or use defaults for Tauri/Vite
cors_origins_env = os.getenv("CORS_ORIGINS")
if cors_origins_env:
    origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "tauri://localhost",
        "http://tauri.localhost",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cripta-backend", "version": "0.1.0"}

@app.get("/status")
async def status():
    return {
        "database": "ready" if db else "not_initialized",
        "orchestrator": "ready" if orchestrator else "not_initialized"
    }

@app.get("/model/active")
async def get_active_model():
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Backend not ready")
    return {"active_model": orchestrator.active_model}

@app.post("/model/active")
async def set_active_model(data: dict):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Backend not ready")
    model = data.get("model")
    if not model:
        raise HTTPException(status_code=400, detail="Model name required")
    orchestrator.active_model = model
    return {"success": True, "active_model": orchestrator.active_model}

@app.post("/action", response_model=ActionResponse)
async def process_action(action: ActionRequest):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Backend not ready")
    
    try:
        result = await orchestrator.process_action(action)
        return ActionResponse(
            success=True,
            message=result.get("message", ""),
            game_state=result.get("state", {}),
            narrative=result.get("narrative", ""),
            generated_events=result.get("generated_events", []),
            available_actions=result.get("available_actions", []),
            audio_url=result.get("audio_url")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/dice/roll")
def roll_dice(notation: str = "1d20"):
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Backend not ready")
    
    try:
        result = orchestrator.dice_engine.roll(notation)
        return {
            "notation": notation,
            "result": result["total"],
            "rolls": result["rolls"],
            "formula": result["formula"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/campaign/current")
async def get_current_campaign():
    if not db:
        raise HTTPException(status_code=503, detail="Database not ready")
    return await db.get_campaign()

@app.get("/character/current")
async def get_current_character():
    if not db:
        raise HTTPException(status_code=503, detail="Database not ready")
    return await db.get_character()

@app.post("/debug/reset")
async def reset_database(x_admin_token: Annotated[str | None, Header()] = None):
    expected_token = os.getenv("ADMIN_TOKEN")
    if not expected_token or x_admin_token != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not db:
        raise HTTPException(status_code=503, detail="Database not ready")
    await db.reset()
    await db.ensure_default_campaign()
    await db.ensure_default_character()
    return {"success": True, "message": "Database reset"}
