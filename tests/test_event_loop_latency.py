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
async def test_event_loop_latency(tmp_path):
    db_path = str(tmp_path / "test.db")
    db = Database(db_path)
    db.initialize()

    orchestrator = Orchestrator(db)
    action = DummyAction("exploration", "I explore", "p1")

    async def measure_latency():
        latencies = []
        for _ in range(200):
            start = time.time()
            await asyncio.sleep(0.01)
            latencies.append(time.time() - start - 0.01)
        return latencies

    with patch('httpx.AsyncClient.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "The room is dark."}
        # Simulate LLM taking some time
        async def mock_post_impl(*args, **kwargs):
            await asyncio.sleep(0.1)
            return mock_response
        mock_post.side_effect = mock_post_impl

        latency_task = asyncio.create_task(measure_latency())

        tasks = [orchestrator.process_action(action) for _ in range(50)]
        await asyncio.gather(*tasks)

        latencies = await latency_task
        max_latency = max(latencies)
        avg_latency = sum(latencies) / len(latencies)
        print(f"\nMax Event Loop Latency: {max_latency:.4f}s")
        print(f"Avg Event Loop Latency: {avg_latency:.4f}s")

    db.close()
