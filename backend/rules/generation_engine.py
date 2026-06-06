import hashlib
import random
from typing import Any, Dict, List, Optional


class GenerationEngine:
    """Seeded procedural content for the campaign loop."""

    THEMES = ["crypt", "fungal cavern", "sunken shrine", "abandoned barracks"]
    FEATURES = [
        "cracked altar",
        "collapsed archway",
        "rune-scarred door",
        "black-water pool",
        "rusted weapon rack",
    ]
    ENCOUNTERS = [
        {"name": "skeletal guard", "ac": 13, "hp": 7, "bonus_to_hit": 3, "damage": "1d6+1"},
        {"name": "kobold scout", "ac": 12, "hp": 5, "bonus_to_hit": 4, "damage": "1d4+2"},
        {"name": "animated armor fragment", "ac": 15, "hp": 11, "bonus_to_hit": 3, "damage": "1d8"},
    ]
    CLUES = [
        "A draft carries the smell of rain from deeper below.",
        "Fresh scratches mark the stone near the eastern wall.",
        "A half-burned map shows three rooms arranged around a sealed vault.",
    ]

    def __init__(self, seed: str = "campaign_1"):
        self.seed = seed

    def initial_room(self, campaign_id: str) -> Dict[str, Any]:
        return self.generate_room(campaign_id=campaign_id, depth=0, source_room_id=None)

    def generate_room(
        self,
        campaign_id: str,
        depth: int,
        source_room_id: Optional[str],
    ) -> Dict[str, Any]:
        rng = self._rng(campaign_id, str(depth), source_room_id or "start")
        theme = rng.choice(self.THEMES)
        feature = rng.choice(self.FEATURES)
        encounter = rng.choice(self.ENCOUNTERS) if rng.random() < 0.65 else None
        room_id = self._room_id(campaign_id, depth, theme, feature, source_room_id)

        exits = ["north", "east", "south", "west"]
        rng.shuffle(exits)

        return {
            "id": room_id,
            "campaign_id": campaign_id,
            "name": f"{theme.title()} {depth + 1}",
            "depth": depth,
            "description": f"A {theme} chamber dominated by a {feature}.",
            "feature": feature,
            "encounter": encounter,
            "clue": rng.choice(self.CLUES),
            "exits": exits[: rng.randint(1, 3)],
            "source_room_id": source_room_id,
        }

    def available_actions(self, room: Dict[str, Any]) -> List[str]:
        actions = ["look around", "search the room", "move deeper", "take a short rest"]
        if room.get("encounter"):
            actions.insert(0, f"attack the {room['encounter']['name']}")
        return actions

    def _rng(self, *parts: str) -> random.Random:
        key = ":".join([self.seed, *parts])
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return random.Random(int(digest[:16], 16))

    def _room_id(
        self,
        campaign_id: str,
        depth: int,
        theme: str,
        feature: str,
        source_room_id: Optional[str],
    ) -> str:
        raw = f"{campaign_id}:{depth}:{theme}:{feature}:{source_room_id or 'start'}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12]
