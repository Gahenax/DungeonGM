from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class ActionType(str, Enum):
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    INVENTORY = "inventory"
    REST = "rest"

class ActionRequest(BaseModel):
    action_type: ActionType
    description: str
    character_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class GameState(BaseModel):
    current_room: Optional[str] = None
    health: Optional[int] = None

class ActionResponse(BaseModel):
    success: bool
    message: str
    game_state: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None
    audio_url: Optional[str] = None
