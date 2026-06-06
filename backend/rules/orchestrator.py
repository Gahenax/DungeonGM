import os
import asyncio
from typing import Any, Dict

import httpx

from .combat_engine import CombatEngine
from .dice_engine import DiceEngine
from .generation_engine import GenerationEngine


class Orchestrator:
    def __init__(self, database):
        self.db = database
        self.dice_engine = DiceEngine()
        self.combat_engine = CombatEngine(self.dice_engine)
        self.generation_engine = GenerationEngine()
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://cripta-ollama:11434")

    async def process_action(self, action) -> Dict[str, Any]:
        print(f"Action: {action.action_type}: {action.description}")

        try:
            campaign = await asyncio.to_thread(self.db.ensure_default_campaign)
            character = await asyncio.to_thread(self.db.ensure_default_character, campaign["id"])
            room = await asyncio.to_thread(self._ensure_current_room, campaign["id"])

            if action.action_type == "combat":
                result = await self._handle_combat(action, room)
                events = [result]
            elif action.action_type == "exploration":
                result = await self._handle_exploration(campaign["id"], room)
                room = result["room"]
                events = [{"type": "room_generated", "room_id": room["id"]}]
            else:
                result = {
                    "type": action.action_type,
                    "message": "Action recorded",
                    "room": room,
                }
                events = [{"type": "action_recorded", "action_type": action.action_type}]

            state = {
                "campaign_id": campaign["id"],
                "current_room": room["id"],
                "room": room,
                "character": character,
                "result": result,
            }
            narrative = await self._generate_narrative(action, state)

            await asyncio.to_thread(
                self.db.log_action,
                campaign["id"],
                {
                    "character_id": action.character_id,
                    "action_type": action.action_type,
                    "description": action.description,
                    "result": str(result),
                },
            )

            return {
                "message": "Action processed",
                "state": state,
                "narrative": narrative,
                "generated_events": events,
                "available_actions": self.generation_engine.available_actions(room),
                "audio_url": None,
            }
        except Exception as e:
            print(f"Error: {e}")
            return {
                "message": "Error",
                "state": {},
                "narrative": "The dungeon remains silent...",
                "generated_events": [],
                "available_actions": [],
                "audio_url": None,
            }

    def _ensure_current_room(self, campaign_id: str) -> Dict[str, Any]:
        room = self.db.get_current_room(campaign_id)
        if room:
            return room

        room = self.generation_engine.initial_room(campaign_id)
        saved_room = self.db.save_room(room)
        self.db.set_current_room(campaign_id, saved_room["id"])
        return saved_room

    async def _handle_combat(self, action, room) -> Dict[str, Any]:
        encounter = room.get("encounter") or {
            "name": "training shadow",
            "ac": 10,
            "hp": 1,
            "bonus_to_hit": 0,
            "damage": "1d4",
        }
        attacker = {"bonus_to_hit": 2}
        combat_result = self.combat_engine.resolve_attack(
            attacker,
            encounter,
            encounter.get("damage", "1d8"),
        )

        return {
            "type": "combat",
            "action_type": "attack",
            "target": encounter["name"],
            **combat_result,
        }

    async def _handle_exploration(self, campaign_id: str, current_room: Dict[str, Any]) -> Dict[str, Any]:
        next_depth = int(current_room.get("depth", 0)) + 1
        room = self.generation_engine.generate_room(
            campaign_id=campaign_id,
            depth=next_depth,
            source_room_id=current_room["id"],
        )
        saved_room = await asyncio.to_thread(self.db.save_room, room)
        await asyncio.to_thread(self.db.set_current_room, campaign_id, saved_room["id"])
        return {
            "type": "exploration",
            "message": "A new room emerges from the dungeon seed.",
            "room": saved_room,
        }

    async def _generate_narrative(self, action, state) -> str:
        room = state.get("room", {})
        prompt = (
            "You are the dungeon master for a solo D&D game. "
            "Narrate exactly 2 concise sentences in a dark fantasy tone. "
            f"Player action: {action.description}. "
            f"Room: {room.get('name')} - {room.get('description')} "
            f"Rules result: {state.get('result')}."
        )

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": "qwen2.5:1.5b",
                        "prompt": prompt,
                        "stream": False,
                    },
                )
                if resp.status_code == 200:
                    return resp.json().get("response", "")[:500]
        except Exception as e:
            print(f"LLM warning: {e}")

        return self._fallback_narrative(action, state)

    def _fallback_narrative(self, action, state) -> str:
        room = state.get("room", {})
        result = state.get("result", {})
        if result.get("type") == "combat":
            outcome = "lands" if result.get("hit") else "misses"
            return (
                f"Your attack {outcome} against the {result.get('target', 'enemy')}. "
                f"The {room.get('name', 'room')} waits for your next move."
            )
        return (
            f"{room.get('description', 'The dungeon shifts around you')} "
            f"{room.get('clue', 'A quiet omen suggests a path forward')}"
        )
