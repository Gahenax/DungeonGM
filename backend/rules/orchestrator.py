import asyncio
import httpx
from typing import Dict, Any
from .dice_engine import DiceEngine
from .combat_engine import CombatEngine

class Orchestrator:
    def __init__(self, database):
        self.db = database
        self.dice_engine = DiceEngine()
        self.combat_engine = CombatEngine(self.dice_engine)
        self.ollama_host = "http://cripta-ollama:11434"
    
    async def process_action(self, action) -> Dict[str, Any]:
        print(f"🎮 {action.action_type}: {action.description}")
        
        try:
            if action.action_type.upper() == "COMBAT":
                result = await self._handle_combat(action)
            else:
                result = {"message": "Action recorded"}
            
            narrative = await self._generate_narrative(action, result)
            
            self.db.log_action("campaign_1", {
                "character_id": action.character_id,
                "action_type": action.action_type,
                "description": action.description,
                "result": str(result)
            })
            
            return {
                "message": "Action processed",
                "state": result,
                "narrative": narrative,
                "audio_url": None
            }
        except Exception as e:
            print(f"❌ {e}")
            return {
                "message": "Error",
                "state": {},
                "narrative": "The dungeon remains silent...",
                "audio_url": None
            }
    
    async def _handle_combat(self, action) -> Dict[str, Any]:
        roll = self.dice_engine.roll("1d20+2")
        hit = roll['total'] >= 12
        damage = self.dice_engine.roll("1d8+2")['total'] if hit else 0
        
        return {
            "action_type": "attack",
            "roll": roll['total'],
            "hit": hit,
            "damage": damage
        }
    
    async def _generate_narrative(self, action, result) -> str:
        prompt = f"Narrate: {action.description} (Result: {result}). 2 sentences, dark tone."
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "qwen2.5:1.5b",
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "")[:500]
        except Exception as e:
            print(f"⚠️ {e}")
        
        return "The dungeon remains silent..."
