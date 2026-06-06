import asyncio
import time
import pytest
from backend.rules.orchestrator import Orchestrator
from backend.database import Database
from unittest.mock import Mock, patch

class DummyAction:
    def __init__(self, action_type, description, character_id):
        self.action_type = action_type
        self.description = description
        self.character_id = character_id

@pytest.mark.asyncio
async def test_process_action_perf(tmp_path):
    db_path = str(tmp_path / "test.db")
    db = Database(db_path)
    db.initialize()

    orchestrator = Orchestrator(db)

    action = DummyAction(
        action_type="exploration",
        description="I explore the room.",
        character_id="player_1"
    )

    with patch('httpx.AsyncClient.post') as mock_post:
        # Mock LLM response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "The room is dark."}
        mock_post.return_value = mock_response

        start_time = time.time()
        tasks = []
        for _ in range(50):
            tasks.append(orchestrator.process_action(action))

        await asyncio.gather(*tasks)

        end_time = time.time()
        print(f"\nExecution time for 50 concurrent actions: {end_time - start_time:.4f} seconds")

    db.close()
