import pytest
import sqlite3
import json
import sys
from pathlib import Path

# Add backend directory to sys.path to import Database
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import Database

@pytest.fixture
def memory_db():
    """Fixture to provide a clean in-memory database for each test."""
    db = Database(":memory:")
    db.initialize()
    yield db
    db.close()

def test_database_initialization(memory_db):
    """Test that tables are correctly created upon initialization."""
    cursor = memory_db.connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row["name"] for row in cursor.fetchall()}

    expected_tables = {"campaigns", "characters", "actions", "rooms"}
    assert expected_tables.issubset(tables)

def test_ensure_default_campaign(memory_db):
    """Test creating and retrieving the default campaign."""
    campaign = memory_db.ensure_default_campaign()
    assert campaign is not None
    assert campaign["id"] == "campaign_1"
    assert campaign["name"] == "The First Descent"
    assert campaign["visited_rooms"] == []

    # Calling it again should return the same campaign without creating a duplicate
    campaign2 = memory_db.ensure_default_campaign()
    assert campaign2 == campaign

    # Verify in DB
    cursor = memory_db.connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM campaigns")
    count = cursor.fetchone()["count"]
    assert count == 1

def test_get_campaign(memory_db):
    """Test getting a campaign by ID or getting the most recent one."""
    # Initially no campaign
    assert not memory_db.get_campaign()
    assert not memory_db.get_campaign("campaign_1")

    # Create campaign
    memory_db.ensure_default_campaign()

    # Get by ID
    campaign = memory_db.get_campaign("campaign_1")
    assert campaign["id"] == "campaign_1"

    # Get without ID (should return most recent)
    recent_campaign = memory_db.get_campaign()
    assert recent_campaign["id"] == "campaign_1"

def test_ensure_default_character(memory_db):
    """Test creating and retrieving the default character."""
    # Character needs a campaign
    memory_db.ensure_default_campaign()

    character = memory_db.ensure_default_character()
    assert character is not None
    assert character["id"] == "player_1"
    assert character["name"] == "Adventurer"
    assert character["campaign_id"] == "campaign_1"
    assert "torch" in character["equipment"]

    # Calling it again should return the same character
    character2 = memory_db.ensure_default_character()
    assert character2 == character

def test_save_and_get_room(memory_db):
    """Test saving a room and retrieving it."""
    room_data = {
        "id": "room_1",
        "campaign_id": "campaign_1",
        "name": "Entrance Hall",
        "depth": 1,
        "description": "A dusty hall.",
        "encounter": {"type": "monster", "name": "Goblin"},
        "exits": ["north", "east"]
    }

    # Save room
    saved_room = memory_db.save_room(room_data)
    assert saved_room["id"] == "room_1"
    assert saved_room["name"] == "Entrance Hall"

    # Retrieve room
    retrieved_room = memory_db.get_room("room_1")
    assert retrieved_room["id"] == "room_1"
    assert retrieved_room["campaign_id"] == "campaign_1"
    assert retrieved_room["encounter"] == {"type": "monster", "name": "Goblin"}
    assert retrieved_room["exits"] == ["north", "east"]

    # Test updating room
    room_data["description"] = "A clean hall."
    memory_db.save_room(room_data)
    updated_room = memory_db.get_room("room_1")
    assert updated_room["description"] == "A clean hall."

def test_get_nonexistent_room(memory_db):
    """Test getting a room that doesn't exist."""
    assert not memory_db.get_room("nonexistent")
