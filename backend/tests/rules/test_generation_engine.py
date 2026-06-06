import pytest
from backend.rules.generation_engine import GenerationEngine


def test_initial_room_deterministic():
    """Test that generating the initial room is deterministic based on seed and campaign_id."""
    engine1 = GenerationEngine(seed="test_seed")
    engine2 = GenerationEngine(seed="test_seed")

    room1 = engine1.initial_room(campaign_id="campaign_123")
    room2 = engine2.initial_room(campaign_id="campaign_123")

    assert room1 == room2
    assert room1["depth"] == 0
    assert room1["source_room_id"] is None
    assert room1["campaign_id"] == "campaign_123"


def test_generate_room_deterministic():
    """Test that generating any room is deterministic based on seed, depth and campaign_id."""
    engine1 = GenerationEngine(seed="another_seed")
    engine2 = GenerationEngine(seed="another_seed")

    room1 = engine1.generate_room(campaign_id="camp_1", depth=3, source_room_id="room_x")
    room2 = engine2.generate_room(campaign_id="camp_1", depth=3, source_room_id="room_x")

    assert room1 == room2
    assert room1["depth"] == 3
    assert room1["source_room_id"] == "room_x"
    assert room1["campaign_id"] == "camp_1"


def test_generate_room_different_inputs():
    """Test that different inputs produce different rooms."""
    engine = GenerationEngine(seed="seed")

    room1 = engine.generate_room(campaign_id="camp_1", depth=1, source_room_id="start")
    room2 = engine.generate_room(campaign_id="camp_2", depth=1, source_room_id="start")
    room3 = engine.generate_room(campaign_id="camp_1", depth=2, source_room_id="start")

    assert room1["id"] != room2["id"]
    assert room1["id"] != room3["id"]


def test_available_actions_without_encounter():
    """Test available actions when there is no encounter."""
    engine = GenerationEngine()
    room = {"encounter": None}

    actions = engine.available_actions(room)

    assert actions == ["look around", "search the room", "move deeper", "take a short rest"]


def test_available_actions_with_encounter():
    """Test available actions when there is an encounter."""
    engine = GenerationEngine()
    room = {
        "encounter": {
            "name": "goblin"
        }
    }

    actions = engine.available_actions(room)

    assert actions == [
        "attack the goblin",
        "look around",
        "search the room",
        "move deeper",
        "take a short rest"
    ]
