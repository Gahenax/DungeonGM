from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

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
    db.initialize()
    orchestrator = Orchestrator(db)
    print("✅ Ready!")
    yield
    if db:
        db.close()
    print("🛑 Shutdown")

app = FastAPI(
    title="Cripta API",
    description="D&D 5.5 Virtual DM",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
async def roll_dice(notation: str = "1d20"):
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
def get_current_campaign():
    if not db:
        raise HTTPException(status_code=503, detail="Database not ready")
    return db.get_campaign()

@app.get("/character/current")
def get_current_character():
    if not db:
        raise HTTPException(status_code=503, detail="Database not ready")
    return db.get_character()

@app.post("/debug/reset")
async def reset_database():
    if not db:
        raise HTTPException(status_code=503, detail="Database not ready")
    db.reset()
    db.ensure_default_campaign()
    db.ensure_default_character()
    return {"success": True, "message": "Database reset"}
