import pytest
import httpx
from unittest.mock import Mock, AsyncMock, patch

from backend.rules.orchestrator import Orchestrator

class MockAction:
    def __init__(self, action_type, description, character_id="char_1", campaign_id="camp_1"):
        self.action_type = action_type
        self.description = description
        self.character_id = character_id
        self.campaign_id = campaign_id

@pytest.fixture
def mock_db():
    db = Mock()
    db.ensure_default_campaign.return_value = {"id": "camp_1"}
    db.ensure_default_character.return_value = {"id": "char_1"}
    db.get_current_room.return_value = {
        "id": "room_1",
        "name": "Starting Room",
        "description": "A dark, empty space.",
        "depth": 0,
        "encounter": {"name": "goblin", "ac": 12, "hp": 5, "damage": "1d6"}
    }
    db.get_campaign.return_value = {"id": "camp_1"}
    db.get_character.return_value = {"id": "char_1"}
    db.save_room.return_value = {"id": "room_2", "name": "Next Room"}
    return db

@pytest.fixture
def orchestrator(mock_db):
    return Orchestrator(mock_db)


@pytest.mark.asyncio
async def test_process_action_combat(orchestrator, mock_db):
    orchestrator.combat_engine.resolve_attack = Mock(return_value={"hit": True, "damage": 5})
    # Mock LLM generation to bypass real API call
    orchestrator._generate_narrative = AsyncMock(return_value="A mighty blow is struck!")

    action = MockAction("combat", "I attack the goblin with my sword")
    result = await orchestrator.process_action(action)

    assert result["message"] == "Action processed"
    assert result["state"]["result"]["type"] == "combat"
    assert result["state"]["result"]["hit"] is True
    assert result["state"]["result"]["damage"] == 5
    assert result["state"]["result"]["target"] == "goblin"

    mock_db.log_action.assert_called_once()
    logged_action = mock_db.log_action.call_args[0][1]
    assert logged_action["action_type"] == "combat"

@pytest.mark.asyncio
async def test_process_action_exploration(orchestrator, mock_db):
    orchestrator.generation_engine.generate_room = Mock(return_value={"id": "room_2", "name": "Next Room", "depth": 1})
    orchestrator._generate_narrative = AsyncMock(return_value="You enter a new room.")

    action = MockAction("exploration", "I walk down the hallway")
    result = await orchestrator.process_action(action)

    assert result["message"] == "Action processed"
    assert result["state"]["result"]["type"] == "exploration"
    assert result["state"]["result"]["room"]["id"] == "room_2"

    # Verify room generation logic
    orchestrator.generation_engine.generate_room.assert_called_once()
    mock_db.save_room.assert_called_once()
    mock_db.set_current_room.assert_called_once_with("camp_1", "room_2")

@pytest.mark.asyncio
async def test_process_action_generic(orchestrator, mock_db):
    orchestrator._generate_narrative = AsyncMock(return_value="You rest by the fire.")

    action = MockAction("rest", "I take a short rest")
    result = await orchestrator.process_action(action)

    assert result["message"] == "Action processed"
    assert result["state"]["result"]["type"] == "rest"
    assert result["state"]["result"]["message"] == "Action recorded"

    mock_db.log_action.assert_called_once()
    logged_action = mock_db.log_action.call_args[0][1]
    assert logged_action["action_type"] == "rest"

@pytest.mark.asyncio
async def test_process_action_error(orchestrator, mock_db):
    # The snippet indicates it calls mock_db.get_campaign, mock_db.get_character and raises ValueError if campaign not found.
    # The full file actually uses ensure_default_campaign, but let's test general error handling here too.
    mock_db.ensure_default_campaign.side_effect = Exception("Database connection failed")

    action = MockAction("combat", "I attack")
    result = await orchestrator.process_action(action)

    assert result["message"] == "Error"
    assert result["narrative"] == "The dungeon remains silent..."
    assert result["state"] == {}
    assert result["generated_events"] == []

@pytest.mark.asyncio
async def test_generate_narrative_success(orchestrator):
    # Mock HTTP client for successful LLM response
    class MockResponse:
        status_code = 200
        def json(self):
            return {"response": "The LLM generated a spooky narrative."}

    mock_client = AsyncMock()
    mock_client.post.return_value = MockResponse()

    # We need to mock the AsyncClient context manager
    with patch('httpx.AsyncClient', return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        action = MockAction("combat", "I attack")
        state = {"room": {"name": "Cave"}, "result": {"type": "combat"}}
        narrative = await orchestrator._generate_narrative(action, state)

        assert narrative == "The LLM generated a spooky narrative."
        mock_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_generate_narrative_fallback(orchestrator):
    # Mock HTTP client for failed LLM response
    class MockResponse:
        status_code = 500

    mock_client = AsyncMock()
    mock_client.post.return_value = MockResponse()

    # We need to mock the AsyncClient context manager
    with patch('httpx.AsyncClient', return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        action = MockAction("combat", "I attack")
        state = {"room": {"name": "Cave"}, "result": {"type": "combat", "hit": True, "target": "orc"}}
        narrative = await orchestrator._generate_narrative(action, state)

        # Should use fallback narrative
        assert "Your attack lands against the orc." in narrative
        assert "The Cave waits for your next move." in narrative

@pytest.mark.asyncio
async def test_generate_narrative_exception(orchestrator):
    # Mock HTTP client to raise exception
    mock_client = AsyncMock()
    mock_client.post.side_effect = Exception("Connection timeout")

    # We need to mock the AsyncClient context manager
    with patch('httpx.AsyncClient', return_value=mock_client) as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        action = MockAction("exploration", "I look around")
        state = {"room": {"description": "A dusty hall.", "clue": "Footprints head north."}, "result": {"type": "exploration"}}
        narrative = await orchestrator._generate_narrative(action, state)

        # Should use fallback narrative
        assert narrative == "A dusty hall. Footprints head north."
