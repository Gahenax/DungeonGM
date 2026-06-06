import pytest
import pytest_asyncio
from backend.database import Database

@pytest_asyncio.fixture
async def db():
    database = Database(":memory:")
    await database.initialize()
    yield database
    await database.close()

@pytest.mark.asyncio
async def test_database_initialization(db):
    """Test that tables are correctly created upon initialization."""
    cursor = await db.connection.cursor()
    await cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row["name"] for row in await cursor.fetchall()}

    expected_tables = {"campaigns", "characters", "actions", "rooms"}
    assert expected_tables.issubset(tables)

@pytest.mark.asyncio
async def test_ensure_default_campaign(db):
    """Test creating and retrieving the default campaign."""
    campaign = await db.ensure_default_campaign()
    assert campaign is not None
    assert campaign["id"] == "campaign_1"
    assert campaign["name"] == "The First Descent"
    assert campaign["visited_rooms"] == []

    # Calling it again should return the same campaign without creating a duplicate
    campaign2 = await db.ensure_default_campaign()
    assert campaign2 == campaign

    # Verify in DB
    cursor = await db.connection.cursor()
    await cursor.execute("SELECT COUNT(*) as count FROM campaigns")
    row = await cursor.fetchone()
    assert row["count"] == 1

@pytest.mark.asyncio
async def test_get_campaign(db):
    """Test getting a campaign by ID or getting the most recent one."""
    # Initially no campaign
    assert not await db.get_campaign()
    assert not await db.get_campaign("campaign_1")

    # Create campaign
    await db.ensure_default_campaign()

    # Get by ID
    campaign = await db.get_campaign("campaign_1")
    assert campaign["id"] == "campaign_1"

    # Get without ID (should return most recent)
    recent_campaign = await db.get_campaign()
    assert recent_campaign["id"] == "campaign_1"

@pytest.mark.asyncio
async def test_ensure_default_character(db):
    """Test creating and retrieving the default character."""
    # Character needs a campaign
    await db.ensure_default_campaign()

    character = await db.ensure_default_character()
    assert character is not None
    assert character["id"] == "player_1"
    assert character["name"] == "Adventurer"
    assert character["campaign_id"] == "campaign_1"
    assert "torch" in character["equipment"]

    # Calling it again should return the same character
    character2 = await db.ensure_default_character()
    assert character2 == character

@pytest.mark.asyncio
async def test_save_and_get_room(db):
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
    saved_room = await db.save_room(room_data)
    assert saved_room["id"] == "room_1"
    assert saved_room["name"] == "Entrance Hall"

    # Retrieve room
    retrieved_room = await db.get_room("room_1")
    assert retrieved_room["id"] == "room_1"
    assert retrieved_room["campaign_id"] == "campaign_1"
    assert retrieved_room["encounter"] == {"type": "monster", "name": "Goblin"}
    assert retrieved_room["exits"] == ["north", "east"]

    # Test updating room
    room_data["description"] = "A clean hall."
    await db.save_room(room_data)
    updated_room = await db.get_room("room_1")
    assert updated_room["description"] == "A clean hall."

@pytest.mark.asyncio
async def test_get_nonexistent_room(db):
    """Test getting a room that doesn't exist."""
    assert not await db.get_room("nonexistent")
