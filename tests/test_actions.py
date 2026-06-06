import sys
import os
from pathlib import Path

# Add backend directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi.testclient import TestClient
import pytest
from unittest.mock import AsyncMock, patch

from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200

def test_process_action_success():
    with TestClient(app) as client:
        with patch("main.orchestrator.process_action", new_callable=AsyncMock) as mock_process_action:
            mock_process_action.return_value = {
                "message": "Action successfully processed",
                "state": {"campaign_id": "test_camp"},
                "narrative": "You attack the goblin and deal 5 damage.",
                "generated_events": [],
                "available_actions": ["move", "attack"],
                "audio_url": None
            }
            response = client.post("/action", json={
                "action_type": "combat",
                "description": "I attack the goblin",
                "character_id": "char1"
            })
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Action successfully processed"
            assert data["game_state"] == {"campaign_id": "test_camp"}
            mock_process_action.assert_called_once()

def test_process_action_backend_not_ready():
    with TestClient(app) as client:
        with patch("main.orchestrator", None):
            response = client.post("/action", json={
                "action_type": "combat",
                "description": "I attack the goblin",
                "character_id": "char1"
            })
            assert response.status_code == 503
            assert response.json()["detail"] == "Backend not ready"

def test_process_action_exception():
    with TestClient(app) as client:
        with patch("main.orchestrator.process_action", new_callable=AsyncMock) as mock_process_action:
            mock_process_action.side_effect = Exception("Test error")
            response = client.post("/action", json={
                "action_type": "combat",
                "description": "I attack the goblin",
                "character_id": "char1"
            })
            assert response.status_code == 400
            assert response.json()["detail"] == "Test error"
