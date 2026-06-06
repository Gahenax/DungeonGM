from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


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
    campaign_id: Optional[str] = None
    current_room: Optional[str] = None
    health: Optional[int] = None
    room: Optional[Dict[str, Any]] = None
    character: Optional[Dict[str, Any]] = None


class ActionResponse(BaseModel):
    success: bool
    message: str
    game_state: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None
    generated_events: Optional[List[Dict[str, Any]]] = None
    available_actions: Optional[List[str]] = None
    audio_url: Optional[str] = None
