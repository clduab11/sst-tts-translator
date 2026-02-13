"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sst_tts_translator.api.server import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "SST/TTS Translator"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_translate_prompt_endpoint():
    """Test prompt translation endpoint."""
    response = client.post(
        "/api/translate-prompt",
        json={
            "text": "create a user service",
            "task_type": "code_generation",
            "include_cot": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "structured_prompt" in data
